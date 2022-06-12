from .transformation import Transformation
from subprocess import check_output

class Convert_2PNG_ImageMagick(Transformation):

    def apply(self, src: str, dst: str, **options):
        dst += '.png'
        check_output(['convert', src, dst])
        return dst
