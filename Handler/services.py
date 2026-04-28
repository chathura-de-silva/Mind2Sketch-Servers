from enum import Enum
class jobType(Enum):
    GENERATE = 1
    PRE_MIX = 2
    PRE_MAPPER = 3


def random_generator(count: int):
    # This function generates 'count' random images and returns them as a list
    images = []
    for _ in range(count):
        image = "random_image_data"
        images.append(image)
    return images