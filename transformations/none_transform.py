from .transformation import Transformation
from PIL import Image
import shutil

class NoneTransformation(Transformation):

    def apply(self, src: str, dst: str, **options) -> None:
        shutil.copy(src, dst)
        return dst


NoneTransformation.__name__ = 'None'