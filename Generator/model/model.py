import urllib.request


class Model:
    def __init__(self):
        self.model = None

    def load(self):
        print("Loading model...")
       # loading model 
        print("Model loaded.")
        return

    def predict_w(self, latent_vector):  # Dummy function to simulate prediction, replace with actual model inference logic
       print("Running ", len(latent_vector), "dimensional vector through the model...")
       hex_data = urllib.request.urlopen(f"https://robohash.org/{''.join(str(x) for x in latent_vector[:2])}.png").read().hex().upper()
       dummy_blob = bytes.fromhex(f"{hex_data}")
       return dummy_blob

    def predict_s(self, latent_vector):  # Dummy function to simulate prediction, replace with actual model inference logic (for style space generation)
       print("Running ", len(latent_vector), "dimensional vector through the model...")
       hex_data = urllib.request.urlopen(f"https://robohash.org/{''.join(str(x) for x in latent_vector[:2])}.png").read().hex().upper()
       dummy_blob = bytes.fromhex(f"{hex_data}")
       return dummy_blob

model_manager = Model()