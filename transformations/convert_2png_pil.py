from .transformation import Transformation
from PIL import Image

class Convert_2PNG_PIL(Transformation):

    def apply(self, src: str, dst: str, **options):
        img = Image.open(src)
        dst += '.png'
        img.save(dst)
        return dst
