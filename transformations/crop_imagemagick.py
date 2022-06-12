from .transformation import Transformation
from PIL import Image
from subprocess import check_output
from .crop_pil import randrange

class Crop_ImageMagick(Transformation):

    def __init__(self) -> None:
        self.random = True
        self.start_x = randrange(0.1, 0.4)
        self.start_y = randrange(0.1, 0.4)
        self.end_x = randrange(0.6, 0.9)
        self.end_y = randrange(0.6, 0.9)

    def apply(self, src: str, dst: str, **options):
        img = Image.open(src)
        start = (img.width * self.start_x, img.height * self.start_y)
        end = (img.width * self.end_x, img.height * self.end_y)
        size = (end[0] - start[0], end[1] - start[1])
        start = tuple(map(int, start))
        size = tuple(map(int, size))
        check_output(['convert', src, '-crop', f'{size[0]}x{size[1]}+{start[0]}+{start[1]}', dst])
        return dst
