import torch


class Clip2StyleMapper(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(512, 1024),
            torch.nn.ReLU(),
            torch.nn.Linear(1024, 2048),
            torch.nn.ReLU(),
            torch.nn.Linear(2048, 6048),
        )

    def forward(self, x):
        return self.net(x)


class StyleAffineMapper(torch.nn.Module):
    def __init__(self, mapping, affines):
        super().__init__()
        self.mapping = mapping
        self.affines = torch.nn.ModuleList(affines)

    def forward(self, z, truncation=0.5):
        w = self.mapping(z, None, truncation_psi=truncation)  # shape [batch, 14, 512]
        return self.apply_affines(w)
    
    def apply_affines(self, w):
        outputs = []

        # Handle First Block
        outputs.append(self.affines[0](w[:, 0]))  # conv1
        outputs.append(self.affines[1](w[:, 0]))  # toRGB

        # Rest of the blocks
        w_idx = 1
        affine_idx = 2
        for _ in range(8):
            # conv0
            outputs.append(self.affines[affine_idx](w[:, w_idx]))
            # conv1
            outputs.append(self.affines[affine_idx + 1](w[:, w_idx + 1]))
            # toRGB (reuses the second w vector of this block)
            outputs.append(self.affines[affine_idx + 2](w[:, w_idx + 1]))

            w_idx += 2
            affine_idx += 3

        return outputs