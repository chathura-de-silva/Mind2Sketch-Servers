import torch

class StyleAffineMapper(torch.nn.Module):
    def __init__(self, mapping, affines):
        super().__init__()
        self.mapping = mapping
        self.affines = torch.nn.ModuleList(affines)

    def forward(self, z, truncation=0.5):
        w = self.mapping(z, None, truncation_psi=truncation)  # shape [batch, 14, 512]

        outputs = []

        # Handle First Block
        outputs.append(self.affines[0](w[:, 0]))  # conv1
        outputs.append(self.affines[1](w[:, 1]))  # toRGB

        # Rest of the blocks
        w_idx = 2
        affine_idx = 2
        for _ in range(6):
            # conv0
            outputs.append(self.affines[affine_idx](w[:, w_idx]))
            # conv1
            outputs.append(self.affines[affine_idx + 1](w[:, w_idx + 1]))
            # toRGB (reuses the second w vector of this block)
            outputs.append(self.affines[affine_idx + 2](w[:, w_idx + 1]))

            w_idx += 2
            affine_idx += 3

        return outputs
    
class StyleSynthesisNetwork(torch.nn.Module):
    def __init__(self, synthesis):
        super().__init__()
        self.synthesis = synthesis
        
        for name, module in self.synthesis.named_modules():
            if hasattr(module, 'affine'):
                module.affine = torch.nn.Identity()

    def forward(self, precomputed_styles):

        style_idx = 0
        
        def hooked_forward(module, input):
            nonlocal style_idx
            new_input = list(input)
            new_input[1] = precomputed_styles[style_idx]
            style_idx += 1
            return tuple(new_input)

        hooks = []
        for name, module in self.synthesis.named_modules():
            if hasattr(module, 'affine'):
                hooks.append(module.register_forward_pre_hook(hooked_forward)) # pre-hook to replace the style input with precomputed styles

        try:
            dummy_ws = torch.zeros(precomputed_styles[0].shape[0],
                                   self.synthesis.num_ws, 512).to(precomputed_styles[0].device) # use a dummy tensor since styles are loaded via hooks
            img = self.synthesis(dummy_ws)
        finally:
            for h in hooks:
                h.remove()
                
        return img