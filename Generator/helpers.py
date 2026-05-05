import numpy as np
import torch
from PIL import Image
import io

STYLE_SHAPES = [512] * 15 + [256] * 3 + [128] * 3 + [64] * 3 + [32] * 2
NUM_LAYERS = 26

def tensor_to_blob(img_tensor: torch.Tensor, fmt: str = "JPEG") -> bytes:
    """Convert a [1, 3, H, W] float tensor (range −1…1) to an image blob.

    Args:
        img_tensor: Output of StyleSynthesisNetwork, shape [1, 3, H, W].
        fmt: Pillow image format string (default 'JPEG').

    Returns:
        Raw image bytes.
    """
    # De-normalise: [-1, 1] → [0, 255]
    img = (img_tensor.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255)
    img_np = img[0].detach().cpu().to(torch.uint8).numpy()
    pil_img = Image.fromarray(img_np)

    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return buf.getvalue()

def split_s(
    style_direction_flattened: np.ndarray,
    device: torch.device = torch.device("cuda"),
) -> list:
    start=0
    style_direction=[]

    style_shapes = [512] * 15 + [256] * 3 + [128] * 3 + [64] * 3 + [32] * 2
    
    for i in range(26):
        layer_len=style_shapes[i]
        end=start+layer_len
        style=style_direction_flattened[start:end]
        start=end
        style = torch.tensor(style)
        style_2d = style.unsqueeze(0)

        style_direction.append(style_2d.detach().clone().float().to(device))
    return style_direction