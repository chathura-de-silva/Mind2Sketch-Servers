from pathlib import Path
import urllib.request
import torch
import numpy as np
import dnnlib
import legacy
from inference import StyleSynthesisNetwork, run_inference
import dnnlib          # noqa
import torch_utils     # noqa
_MODULE_DIR = Path(__file__).resolve().parent
NETWORK_PKL = str(_MODULE_DIR / "ffhq.pkl")

class Model:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.style_synthesis = None

    def load(self):
        print("Loading model...")
        with dnnlib.util.open_url(NETWORK_PKL) as f:
            G = legacy.load_network_pkl(f)["G_ema"].to(self.device)
        self.style_synthesis = StyleSynthesisNetwork(G.synthesis).to(self.device)
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
       return run_inference(
           flat_style_vector=np.array(flat_style_vector, dtype=np.float32),
           style_synthesis=self.style_synthesis,
           device=self.device,
       )

model_manager = Model()