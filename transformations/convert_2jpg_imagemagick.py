from .transformation import Transformation
from PIL import Image
from subprocess import check_output

class Convert_2JPG_ImageMagick(Transformation):

    def apply(self, src: str, dst: str, **options):
        dst += '.jpg'
        check_output(['convert', src, dst])
        return dst
