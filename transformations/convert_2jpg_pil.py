from .transformation import Transformation
from PIL import Image

class Convert_2JPG_PIL(Transformation):

    def apply(self, src: str, dst: str, **options):
        img = Image.open(src)
        dst += '.jpg'
        img.save(dst)
        return dst
