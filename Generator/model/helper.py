import numpy as np
import torch
from PIL import Image
import io
from config import settings

STYLE_SHAPES = [512] * 12 + [256] * 3 + [128] * 3 + [64] * 2
NUM_LAYERS = 20

def tensor_to_blob(img_tensor: torch.Tensor, fmt: str = settings.image_content_type.value) -> bytes:
  
    # De-normalise: [-1, 1] → [0, 255]
    img = (img_tensor.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255)
    img_np = img[0].detach().cpu().to(torch.uint8).numpy()
    pil_img = Image.fromarray(img_np)

    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return buf.getvalue()

def style_vector_deserializer(
    style_direction_flattened: np.ndarray,
    device: torch.device = torch.device("cuda"),
) -> list:
    start=0
    style_direction=[]
    
    for i in range(20):
        layer_len=STYLE_SHAPES[i]
        end=start+layer_len
        style=style_direction_flattened[start:end]
        start=end
        style = torch.tensor(style)
        style_2d = style.unsqueeze(0)

        style_direction.append(style_2d.detach().clone().float().to(device))
    return style_direction