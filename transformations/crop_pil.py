from .transformation import Transformation
from PIL import Image
import random


def randrange(start, stop):
    return (stop - start) * random.random() + start    

class Crop_PIL(Transformation):

    def __init__(self) -> None:
        self.random = True
        self.start_x = randrange(0.1, 0.4)
        self.start_y = randrange(0.1, 0.4)
        self.end_x = randrange(0.6, 0.9)
        self.end_y = randrange(0.6, 0.9)


    def do_apply(self, src: Image) -> Image:
        box = (src.width * self.start_x, src.height * self.start_y, src.width * self.end_x, src.height * self.end_y)
        box = tuple(map(int, box))
        return src.crop(box)