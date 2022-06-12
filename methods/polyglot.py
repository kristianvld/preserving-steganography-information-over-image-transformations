from PIL import Image
from transformations.transformation import Transformation
from .method import Method


class Polyglot(Method):

    """
    magic_bytes just a random magic byte sequence used to detect our data payload. Strictly speaking this is not needed, but makes searching for our data easier.

    By default a random byte sequence has been chosen, in this case the first 12 digits of pi.
    """
    def __init__(self, magic_bytes=b'\x31\x41\x59\x26\x53\x58') -> None:
        self.magic_bytes = magic_bytes
    
    def apply(self, msg: bytes, src: str, dst: str, transformation: Transformation = None) -> None:
        with open(src, 'rb') as input:
            with open(dst, 'wb') as output:
                data = input.read()
                data += self.magic_bytes + msg
                output.write(data)

    def extract(self, img: str, transformation: Transformation) -> bytes:
        with open(img, 'rb') as input:
            data = input.read()
            try:
                index = data.index(self.magic_bytes)
                payload = data[index + len(self.magic_bytes):]
                return payload
            except ValueError:
                return b''