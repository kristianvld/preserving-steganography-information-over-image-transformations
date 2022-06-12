from PIL import Image
import os

from transformations.transformation import Transformation

class Method:

    def apply(self, msg: bytes, src: str, dst: str, transformation: Transformation = None) -> None:
        func_name = f'do_apply_{transformation.__class__.__name__.lower()}'
        func = getattr(self, func_name, None)
        if not func:
            func_name += '_raw'
            func = getattr(self, func_name, None)
            if not func:
                raise NotImplementedError(f'Function {func_name} is not implemented in method {self.__class__.__name__}')
            func(msg, src, dst, transformation)
            if not os.path.isfile(dst):
                raise FileNotFoundError(f'Function {func_name} did not save any output file to {dst}')
            return

        img = Image.open(src)
        transformed = func(msg, img, transformation)
        transformed.save(dst, quality='maximum')

    def do_apply_transformname(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        raise NotImplementedError(f'Function do_apply_none is not implemented in method {self.__class__.__name__}')

    def do_apply_transformname_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        raise NotImplementedError(f'Function do_apply_none_raw is not implemented in method {self.__class__.__name__}')    

    def extract(self, img: str, transformation: Transformation) -> bytes:
        img = Image.open(img)
        return self.do_extract(img, transformation)

    def do_extract(self, img: Image, transformation: Transformation) -> bytes:
        raise NotImplementedError()