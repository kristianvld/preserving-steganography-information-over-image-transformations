from PIL import Image

class Transformation:

    def apply(self, src: str, dst: str, **options) -> str:
        img = Image.open(src)
        transformed = self.do_apply(img, **options)
        transformed.save(dst)
        return dst

    def do_apply(self, src: Image, **options) -> Image:
        raise NotImplementedError()
