from pathlib import Path
import urllib.request
import torch
import dnnlib
import legacy
import dnnlib
from networks import StyleAffineMapper, StyleSynthesisNetwork
from helpers import split_s, tensor_to_blob

_MODULE_DIR = Path(__file__).resolve().parent
NETWORK_PKL = str(_MODULE_DIR / "ffhq.pkl")
class Model:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.style_synthesis = None
        self.affine_mapper = None

    def load(self):
        print("Loading model...")
        with dnnlib.util.open_url(NETWORK_PKL) as f:
            G = legacy.load_network_pkl(f)["G_ema"].to(self.device)
        self.style_synthesis = StyleSynthesisNetwork(G.synthesis).to(self.device)

        affines = []
        for name, module in G.synthesis.named_modules():
            if hasattr(module, "affine"):
                affines.append(module.affine)

        self.affine_mapper = StyleAffineMapper(G.mapping, affines).to(self.device)
        return

    def predict_w(self, latent_vector):  # Dummy function to simulate prediction, replace with actual model inference logic
       print("Running ", len(latent_vector), "dimensional vector through the model...")
       hex_data = urllib.request.urlopen(f"https://robohash.org/{''.join(str(x) for x in latent_vector[:2])}.png").read().hex().upper()
       dummy_blob = bytes.fromhex(f"{hex_data}")
       return dummy_blob

    def predict_s(self, flat_style_vector):
        print("Running ", len(flat_style_vector), "dimensional vector through the model...")
        if self.style_synthesis is None:
            raise RuntimeError("Style synthesis network is not loaded. Call load() before predict_s().")
        
        flat_style_vector = torch.tensor(flat_style_vector, dtype=torch.float32, device=self.device)
        
        if flat_style_vector.ndim != 1:
            raise ValueError(
                f"flat_style_vector must be 1-D, got shape {flat_style_vector.shape}"
            )
        
        styles = split_s(flat_style_vector, device=self.device)

        with torch.no_grad():
            img_tensor = self.style_synthesis(styles)

        blob = tensor_to_blob(img_tensor, fmt="JPEG")

        return blob

model_manager = Model()