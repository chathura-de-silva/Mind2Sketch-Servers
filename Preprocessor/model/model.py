from pathlib import Path
import torch
import clip
import dnnlib
import legacy
from . import networks
from typing import cast
import numpy as np
import copy

_MODULE_DIR = Path(__file__).resolve().parent
NETWORK_PKL = str(_MODULE_DIR / "ffsl.pkl")
CLIP2STYLE_MATRIX = str(_MODULE_DIR / "fs3_256.npy")
CLIP_NEUTRAL_TEXT = "a face"


class Model:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.affine_mapper = None
        self.clip_model = None
        self.clip2style_mapper = None
        self.neutral_clip_embedding = None
        self.neutral_style_vector = None

    def load(self):
        with dnnlib.util.open_url(NETWORK_PKL) as f:
            network = cast(dict, legacy.load_network_pkl(f))
            G = network["G_ema"].to(self.device)

        affines = []
        for name, module in G.synthesis.named_modules():
            if hasattr(module, "affine"):
                affines.append(module.affine)

        self.affine_mapper = networks.StyleAffineMapper(G.mapping, affines).to(self.device)

        self.clip_model, _ = clip.load("ViT-B/32", device=self.device, jit=False)
        self.clip_model.eval()

        self.clip2style_mapper = np.load(CLIP2STYLE_MATRIX)

        with torch.no_grad():
            tokens = clip.tokenize([CLIP_NEUTRAL_TEXT]).to(self.device)
            self.neutral_clip_embedding = self.clip_model.encode_text(tokens).float()
        
        self.neutral_style_vector = self.z_to_s(torch.zeros(1, 512, device=self.device))

    def random_z_to_s(self, seed):
        g = torch.Generator(device=self.device)
        g.manual_seed(int(seed))
        z = torch.randn(1, 512, generator=g, device=self.device)
        return self.z_to_s(z)
    
    def z_to_s(self, z):
        if self.affine_mapper is None:
            raise ValueError("Affine Mapper model not loaded yet!")

        styles = self.affine_mapper(z, truncation=0.5)
        flat_style_vector = torch.cat([s.flatten() for s in styles], dim=0).cpu().detach().numpy()
        return flat_style_vector.tolist()

    def text_to_style_direction(self, text_prompt: str) -> list:
        
        def get_style_direction(clip2styles_matrix,clip_direction,top_styles):
            '''get the direction in the style space (boundary) with the precomputed clip2styles matrix.'''
            style_direction_flattened=np.dot(clip2styles_matrix,clip_direction[0])
            
            style_direction_flattened_2=copy.copy(style_direction_flattened)
            threshold_idx = np.argsort(np.abs(style_direction_flattened))[:-int(top_styles)]
            select = np.zeros(len(style_direction_flattened), dtype=bool)
            select[threshold_idx] = True

            style_direction_flattened_2[select] = 0
            tmp=np.abs(style_direction_flattened_2).max()
            print('max value before normalization:',tmp)
            style_direction_flattened_2/= (tmp + 1e-5)
            
            style_direction=split_s(style_direction_flattened_2)
            print('num of channels being manipulated:',top_styles)
            return style_direction

        def split_s(flat_style_vector):
             start = 0
             style_direction = []
             mindexs = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15]
             style_shapes = [512] * 12 + [256] * 3 + [128] * 3 + [64] * 2
             for i in range(20):
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

            target = text_embedding / (text_embedding.norm(dim=1, keepdim=True) + 1e-8)
            neutral = self.neutral_clip_embedding / (self.neutral_clip_embedding.norm(dim=1, keepdim=True) + 1e-8)
            direction = target - neutral
            direction = direction / (direction.norm(dim=1, keepdim=True) + 1e-8)

            style_vector = get_style_direction(self.clip2style_mapper,direction,100)
            flat_style_vector = style_vector.flatten().cpu().detach().numpy().tolist()
            final_style_vector = split_s(flat_style_vector)
        return final_style_vector.detach().cpu().numpy().tolist()

model_manager = Model()