from pathlib import Path
import torch
import dnnlib
import legacy
from . import networks
from typing import cast

_MODULE_DIR = Path(__file__).resolve().parent
NETWORK_PKL = str(_MODULE_DIR / "ffhq.pkl")

class Model:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.affine_mapper = None

    def load(self):
        with dnnlib.util.open_url(NETWORK_PKL) as f:
           network = cast(dict, legacy.load_network_pkl(f))
           G = network["G_ema"].to(self.device)

        affines = []
        for name, module in G.synthesis.named_modules():
            if hasattr(module, "affine"):
                affines.append(module.affine)

        self.affine_mapper = networks.StyleAffineMapper(G.mapping, affines).to(self.device)
        return

    def random_z_to_s(self, seed): 
        if  self.affine_mapper is None:
           raise ValueError("Affine Mapper or Generator model not loaded yet!")
        
        g = torch.Generator(device=self.device)
        g.manual_seed(int(seed))
        z = torch.randn(1, 512, generator=g, device=self.device)
      
        styles = self.affine_mapper(z,truncation=0.5)
        flat_style_vector = torch.cat([s.flatten() for s in styles], dim=0).cpu().detach().numpy()
        return flat_style_vector.tolist()

model_manager = Model()