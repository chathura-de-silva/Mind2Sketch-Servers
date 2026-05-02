from enum import Enum
class jobType(Enum):
    GENERATE = 1
    PRE_MIX = 2
    PRE_MAPPER = 3


def random_generator(count: int):
    images = []
    for _ in range(count):
        image = "random_image_data"
        images.append(image)
    return images

def mix_generator():
    # This function generates mixed images and returns them as a list
    images = []
    for _ in range(5):  # Assuming we generate 5 mixed images
        image = "mixed_image_data"
        images.append(image)
    return images

def text_generator(prompt: str, count: int):
    # This function generates images based on text input and returns them as a list
    images = []
    for _ in range(count):
        image = f"text_to_image_data_{prompt}"
        images.append(image)
    return images