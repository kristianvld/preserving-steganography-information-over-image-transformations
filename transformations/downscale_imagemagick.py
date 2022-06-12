from .transformation import Transformation
from PIL import Image
from subprocess import check_output


class Downscale_ImageMagick(Transformation):

    def __init__(self, x = 0.5, y = 0.5) -> None:
        self.x = x
        self.y = y

    def apply(self, src: str, dst: str, **options) -> str:
        img = Image.open(src)
        check_output(['convert', src, '-resize', f'{img.width * self.x}x{img.height * self.y}!', dst])
        return dst