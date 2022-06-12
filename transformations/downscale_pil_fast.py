from .transformation import Transformation
from PIL import Image


class Downscale_PIL_Fast(Transformation):

    def __init__(self, x = 0.5, y = 0.5) -> None:
        self.x = x
        self.y = y

    def do_apply(self, src: Image) -> Image:
        return src.resize((round(src.width * self.x), round(src.height * self.y)), Image.NEAREST)