

def style_mixer(vectors, weights, count):
    if not weights:
        weights = [1.0 / len(vectors)] * len(vectors)

    dim = len(vectors[0])
    new_style_vectors = []

    # Vector 0: weighted mean (guaranteed valid, on manifold)
    mean_vector = [
        sum(weights[j] * vectors[j][i] for j in range(len(vectors)))
        for i in range(dim)
    ]
    new_style_vectors.append(mean_vector)

    # Remaining vectors: weighted interpolations between pairs
    # t spreads evenly from 0 to 1 across remaining count-1 slots
    for k in range(1, count):
        t = k / (count - 1) if count > 1 else 0.5

        # Blend each consecutive pair of input vectors using t and weights
        mixed = [0.0] * dim
        total_weight = 0.0

        for j in range(len(vectors) - 1):
            pair_weight = (weights[j] + weights[j + 1]) / 2
            for i in range(dim):
                mixed[i] += pair_weight * (
                    (1 - t) * vectors[j][i] + t * vectors[j + 1][i]
                )
            total_weight += pair_weight

        # Normalize by total weight to keep scale correct
        new_style_vectors.append([x / total_weight for x in mixed])
    return new_style_vectors