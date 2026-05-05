import io

import numpy as np
import torch
from PIL import Image


MINDEXS = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24]
STYLE_SHAPES = [512] * 15 + [256] * 3 + [128] * 3 + [64] * 3 + [32] * 2
NUM_LAYERS = 26


class StyleSynthesisNetwork(torch.nn.Module):
    """Runs the StyleGAN2 synthesis network with externally supplied style
    vectors injected via forward-pre-hooks (bypasses all affine layers)."""

    def __init__(self, synthesis):
        super().__init__()
        self.synthesis = synthesis
        # Replace every affine sub-module with Identity so the hook is the
        # sole source of styles.
        for _, module in self.synthesis.named_modules():
            if hasattr(module, "affine"):
                module.affine = torch.nn.Identity()

    def forward(self, precomputed_styles):
        style_idx = 0

        def _hook(module, input):
            nonlocal style_idx
            new_input = list(input)
            new_input[1] = precomputed_styles[style_idx]
            style_idx += 1
            return tuple(new_input)

        hooks = []
        for _, module in self.synthesis.named_modules():
            if hasattr(module, "affine"):
                hooks.append(module.register_forward_pre_hook(_hook))

        try:
            dummy_ws = torch.zeros(
                precomputed_styles[0].shape[0],
                self.synthesis.num_ws,
                512,
                device=precomputed_styles[0].device,
            )
            img = self.synthesis(dummy_ws)
        finally:
            for h in hooks:
                h.remove()

        return img  # [B, 3, H, W], values in [-1, 1]

def split_s(
    style_direction_flattened: np.ndarray,
    device: torch.device = torch.device("cuda"),
) -> list:

    start = 0
    style_direction = []

    for i in range(NUM_LAYERS):
        layer_dim = STYLE_SHAPES[i]
        if i in MINDEXS:
            end = start + layer_dim
            style = style_direction_flattened[start:end]
            start = end
        else:
            style = np.zeros(layer_dim, dtype=np.float32)

        style_tensor = (
            torch.tensor(style, dtype=torch.float32)
            .unsqueeze(0)   # → [1, C]
            .to(device)
        )
        style_direction.append(style_tensor)

    return style_direction



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


def run_inference(
    flat_style_vector: np.ndarray,
    style_synthesis: StyleSynthesisNetwork,
    alpha: float = 1.0,
    device: torch.device = torch.device("cuda"),
    output_format: str = "JPEG",
) -> bytes:
    """Take a flattened style vector, split it, run synthesis, return a blob.

    Args:
        flat_style_vector: 1-D numpy array of length 6048 representing a
            style direction or absolute style vector.
        style_synthesis: An initialised StyleSynthesisNetwork instance.
        alpha: Optional scalar multiplied into the style vector before
            synthesis (useful for interpolation / strength control).
        device: Torch device to run on.
        output_format: Image format for the returned blob (e.g. 'JPEG', 'PNG').

    Returns:
        Raw image bytes (JPEG by default).
    """
    if flat_style_vector.ndim != 1:
        raise ValueError(
            f"flat_style_vector must be 1-D, got shape {flat_style_vector.shape}"
        )

  
    vec = flat_style_vector * alpha if alpha != 1.0 else flat_style_vector

    style_layers = split_s(vec, device=device)

    with torch.no_grad():
        img_tensor = style_synthesis(style_layers)

    blob = tensor_to_blob(img_tensor, fmt=output_format)

    return blob