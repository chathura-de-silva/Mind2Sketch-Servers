from pathlib import Path
import sys
import torch
import clip
import torchvision.transforms as transforms
from PIL import Image
from config import LLM_SYSTEM_PROMPT,OLAMA_MODEL_NAME
import dnnlib
import legacy
from . import networks
from typing import Any, cast
import numpy as np
import scipy.ndimage
from facenet_pytorch import MTCNN
from ollama import chat

_MODULE_DIR = Path(__file__).resolve().parent
NETWORK_PKL = str(_MODULE_DIR / "ffhq.pkl")
CLIP2STYLE_WEIGHTS = str(_MODULE_DIR / "mapping_network.pth")
E4E_MODEL_PATH = str(_MODULE_DIR / "e4e_ffhq_encode.pt")
E4E_REPO_PATH = str(_MODULE_DIR.parent / "encoder4editing")
CLIP_NEUTRAL_TEXT = "a face"


class Model:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.affine_mapper = None
        self.clip_model = None
        self.clip2style_mapper = None
        self.neutral_clip_embedding = None
        self.neutral_style_vector = None
        self.e4e_net = None
        self.e4e_transforms = None
        self.mtcnn = None

    def load(self):
        with dnnlib.util.open_url(NETWORK_PKL) as f:
            network = cast(dict, legacy.load_network_pkl(f))
            G = network["G_ema"].to(self.device)

        affines = []
        for name, module in G.synthesis.named_modules():
            if hasattr(module, "affine"):
                affines.append(module.affine)

        self.affine_mapper = networks.StyleAffineMapper(G.mapping, affines).to(
            self.device
        )

        self.clip_model, _ = clip.load("ViT-B/32", device=self.device, jit=False)
        self.clip_model.eval()

        self.clip2style_mapper = networks.Clip2StyleMapper().to(self.device)
        self.clip2style_mapper.load_state_dict(
            torch.load(CLIP2STYLE_WEIGHTS, map_location=self.device)
        )
        self.clip2style_mapper.eval()

        with torch.no_grad():
            tokens = clip.tokenize([CLIP_NEUTRAL_TEXT]).to(self.device)
            self.neutral_clip_embedding = self.clip_model.encode_text(tokens).float()

        self.neutral_style_vector = self.z_to_s(torch.zeros(1, 512, device=self.device))

        # Load E4E model for projection
        sys.path.insert(0, E4E_REPO_PATH)
        if not Path(E4E_MODEL_PATH).exists():
            raise FileNotFoundError(f"E4E  weight file not found at {E4E_MODEL_PATH}. Please ensure the model file exists.")
        from utils.model_utils import load_e4e_standalone
        self.e4e_net = load_e4e_standalone(E4E_MODEL_PATH, str(self.device))
        
        self.e4e_net.eval()
        self.e4e_transforms = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ])

        self.mtcnn = MTCNN(keep_all=True, device=self.device)

    def random_z_to_s(self, seed):
        g = torch.Generator(device=self.device)
        g.manual_seed(int(seed))
        z = torch.randn(1, 512, generator=g, device=self.device)
        return self.z_to_s(z)

    def z_to_s(self, z):
        if self.affine_mapper is None:
            raise ValueError("Affine Mapper model not loaded yet!")

        styles = self.affine_mapper(z, truncation=0.5)
        flat_style_vector = (
            torch.cat([s.flatten() for s in styles], dim=0).cpu().detach().numpy()
        )
        return flat_style_vector.tolist()

    def get_negative_prompt(self, positive_prompt: str) -> str | None:
        response = chat(
            think=False,
            model=OLAMA_MODEL_NAME,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": positive_prompt},
            ],
            options={"num_predict": 256, "temperature": 0.3},
        )
        if response.message.content:
            return str(response.message.content)
        return None

    def text_to_style_direction(
        self, text_prompt: str, negative_prompt: str | None
    ) -> list:

        def split_s(flat_style_vector):
            start = 0
            style_direction = []
            mindexs = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24]
            style_shapes = [512] * 15 + [256] * 3 + [128] * 3 + [64] * 3 + [32] * 2
            for i in range(26):
                if i in mindexs:
                    layer_len = style_shapes[i]
                    end = start + layer_len
                    style = flat_style_vector[start:end]
                    start = end
                else:
                    style = np.zeros(style_shapes[i])
                style = torch.tensor(style, dtype=torch.float32)
                style_direction.append(style)
            return torch.cat([s.view(-1) for s in style_direction]).to(self.device)

        if self.clip_model is None or self.clip2style_mapper is None:
            raise ValueError("Models not loaded yet!")

        with torch.no_grad():
            tokens = clip.tokenize([text_prompt]).to(self.device)
            text_embedding = self.clip_model.encode_text(tokens).float()

            if negative_prompt is not None:
                neg_tokens = clip.tokenize([negative_prompt]).to(self.device)
                neg_embedding = self.clip_model.encode_text(neg_tokens).float()
            else:
                neg_embedding = self.neutral_clip_embedding

            target = text_embedding / (text_embedding.norm(dim=1, keepdim=True) + 1e-8)
            neutral = neg_embedding / (neg_embedding.norm(dim=1, keepdim=True) + 1e-8)
            direction = target - neutral
            direction = direction / (direction.norm(dim=1, keepdim=True) + 1e-8)

            style_vector = self.clip2style_mapper(direction)
            flat_style_vector = style_vector.flatten().cpu().detach().numpy().tolist()
            final_style_vector = split_s(flat_style_vector)
        return final_style_vector.detach().cpu().numpy().tolist()
    
    def detect_crop_and_resize(self, image: Image.Image, output_size: int = 256) -> Image.Image:
        if self.mtcnn is None:
            raise ValueError("MTCNN not loaded yet!")

        result = cast(tuple[Any, Any, Any], self.mtcnn.detect(image, landmarks=True))
        boxes, _, landmarks = result

        if boxes is None or len(boxes) == 0:
            raise ValueError("No face detected in the image.")

        areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
        idx = int(np.argmax(areas))
        lm = landmarks[idx]  # (5, 2): left_eye, right_eye, nose, mouth_left, mouth_right

        left_eye    = np.array(lm[0])
        right_eye   = np.array(lm[1])
        mouth_left  = np.array(lm[3])
        mouth_right = np.array(lm[4])

        eye_avg      = (left_eye + right_eye) * 0.5
        eye_to_eye   = right_eye - left_eye
        mouth_avg    = (mouth_left + mouth_right) * 0.5
        eye_to_mouth = mouth_avg - eye_avg

        x  = eye_to_eye - np.flip(eye_to_mouth) * np.array([-1, 1])
        x /= np.hypot(*x)
        x *= max(np.hypot(*eye_to_eye) * 2.0, np.hypot(*eye_to_mouth) * 1.8)
        y  = np.flip(x) * np.array([-1, 1])
        c  = eye_avg + eye_to_mouth * 0.1
        quad  = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])
        qsize = np.hypot(*x) * 2

        img = image.copy()

        shrink = int(np.floor(qsize / output_size * 0.5))
        if shrink > 1:
            rsize = (
                int(np.rint(float(img.size[0]) / shrink)),
                int(np.rint(float(img.size[1]) / shrink)),
            )
            img    = img.resize(rsize, Image.Resampling.LANCZOS)
            quad  /= shrink
            qsize /= shrink

        border = max(int(np.rint(qsize * 0.1)), 3)
        crop = (
            max(int(np.floor(min(quad[:, 0]))) - border, 0),
            max(int(np.floor(min(quad[:, 1]))) - border, 0),
            min(int(np.ceil(max(quad[:, 0]))) + border, img.size[0]),
            min(int(np.ceil(max(quad[:, 1]))) + border, img.size[1]),
        )
        if crop[2] - crop[0] < img.size[0] or crop[3] - crop[1] < img.size[1]:
            img    = img.crop(crop)
            quad  -= crop[0:2]

        pad = (
            max(-int(np.floor(min(quad[:, 0]))) + border, 0),
            max(-int(np.floor(min(quad[:, 1]))) + border, 0),
            max(int(np.ceil(max(quad[:, 0]))) - img.size[0] + border, 0),
            max(int(np.ceil(max(quad[:, 1]))) - img.size[1] + border, 0),
        )
        if max(pad) > border - 4:
            pad = np.maximum(pad, int(np.rint(qsize * 0.3)))
            img_arr = np.array(img, dtype=np.float32)
            img_arr = np.pad(img_arr, ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)), "reflect")
            h, w, _ = img_arr.shape
            y_grid, x_grid, _ = np.ogrid[:h, :w, :1]
            mask = np.maximum(
                1.0 - np.minimum(
                    np.float32(x_grid) / pad[0],
                    np.float32(w - 1 - x_grid) / pad[2],
                ),
                1.0 - np.minimum(
                    np.float32(y_grid) / pad[1],
                    np.float32(h - 1 - y_grid) / pad[3],
                ),
            )
            blur = qsize * 0.02
            img_arr += (scipy.ndimage.gaussian_filter(img_arr, [blur, blur, 0]) - img_arr) * np.clip(mask * 3.0 + 1.0, 0.0, 1.0)
            img_arr += (np.median(img_arr, axis=(0, 1)) - img_arr) * np.clip(mask, 0.0, 1.0)
            img   = Image.fromarray(np.uint8(np.clip(np.rint(img_arr), 0, 255)), "RGB")
            quad += pad[:2]

        return img.transform(
            (output_size, output_size),
            Image.Transform.QUAD,
            (quad + 0.5).flatten().tolist(),
            Image.Resampling.BICUBIC,
        )

    def project_e4e(self, image: Image.Image) -> torch.Tensor:
        if self.e4e_net is None or self.e4e_transforms is None:
            raise ValueError("E4E model not loaded yet!")

        x = cast(torch.Tensor, self.e4e_transforms(image)).unsqueeze(0).to(self.device).float()

        with torch.no_grad():
            codes = self.e4e_net(x)

        return codes  # [1, 18, 512]

    def w_plus_to_s(self, w_plus: torch.Tensor) -> list:
        # This is being used by the E4E Projection, to map it's W+ output to the Style Space.
        #  w_plus: [1, 18, 512] 
        if self.affine_mapper is None:
            raise ValueError("Affine Mapper model not loaded yet!")
        with torch.no_grad():
            styles = self.affine_mapper.apply_affines(w_plus.to(self.device))
            flat = torch.cat([s.flatten() for s in styles], dim=0).cpu().numpy()
        return flat.tolist()

model_manager = Model()
