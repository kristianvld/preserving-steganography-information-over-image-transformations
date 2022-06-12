from logging import debug
import math
import os
import tempfile
from typing import Callable
from PIL import Image
from transformations.transformation import Transformation
from .method import Method

def to_bin(n, bits):
    return bin(n)[2:].zfill(bits)

class LSB(Method):
    """
    palette = (0,1,2) means place bits in RGB, in that order
    """
    def __init__(self, palette = (0,1,2), bits: int = 2, pixel_loc_mapper: Callable = None) -> None:
        self.bits = bits
        self.palette = list(palette)
        self.pixel_loc_mapper = pixel_loc_mapper or (lambda x, y: (x, y))
    
    def bytes_to_binary(self, msg: bytes, group_size: int):
        bits = ''.join([bin(b)[2:].zfill(8) for b in msg])
        return [int(bits[i:i+group_size], 2) for i in range(0, len(bits), group_size)][::-1]
    

    def do_apply_none(self, msg, img, transformation):
        if len(img.mode) != len(self.palette):
            debug(f'Invalid channel mode {img.mode} and palette config {self.palette}')
            return img

        bits_groups = self.bytes_to_binary(msg, self.bits)

        for _y in range(img.size[1]):
            for _x in range(img.size[0]):
                x, y = self.pixel_loc_mapper(_x, _y)
                _pixel = list(img.getpixel((x, y)))
                for chnl in self.palette:
                    _pixel[chnl] = ((_pixel[chnl] >> self.bits) << self.bits) | bits_groups.pop()
                    img.putpixel((x, y), tuple(_pixel))
                    if len(bits_groups) == 0:
                        return img
        return img
    
    def do_apply_convert_2jpg_pil(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.do_apply_none(msg, src, transformation)
    
    def do_apply_convert_2png_pil(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.do_apply_none(msg, src, transformation)

    def do_apply_convert_2jpg_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.do_apply_none(msg, src, transformation)
    
    def do_apply_convert_2png_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.do_apply_none(msg, src, transformation)
    
    """
    In most cases such as when you downscale to half, quarter etc, then (img * 0.5) * 2 = img
    We can simply downscale, to the target size, apply lsb and then upscale to the original size 
    """
    def do_apply_downscale_pil(self, msg: bytes, src: Image, down: Transformation) -> Image:
        dst_file = tempfile.gettempdir() + '/lsb.png'
        src.save(dst_file)
        down.apply(dst_file, dst_file)
        dst = Image.open(dst_file)

        dst = self.do_apply_crop_pil(msg, dst, down)
        x, y = down.x, down.y
        down.x, down.y = 1 / x, 1 / y
        dst.save(dst_file)
        down.apply(dst_file, dst_file)
        down.x, down.y = x, y
        dst = Image.open(dst_file)
        os.remove(dst_file)

        return dst
    
    def do_apply_downscale_pil_normal(self, msg: bytes, src: Image, down: Transformation) -> Image:
        return self.do_apply_downscale_pil(msg, src, down)
    
    def do_apply_downscale_pil_fast(self, msg: bytes, src: Image, down: Transformation) -> Image:
        return self.do_apply_downscale_pil(msg, src, down)

    def do_apply_downscale_imagemagick(self, msg: bytes, src: Image, down: Transformation) -> Image:
        return self.do_apply_downscale_pil(msg, src, down)

    """
    To combat random cropping, we will repeat the message for the whole image
    """
    def do_apply_crop_pil(self, msg: bytes, src: Image, crop: Transformation) -> Image:
        pixels = src.width * src.height
        bits_per_pixel = self.bits * len(self.palette)
        msg_bit_len = len(msg) * 8
        msg_pixel_len = msg_bit_len / bits_per_pixel
        msg = msg * math.ceil(pixels / msg_pixel_len)
        return self.do_apply_none(msg, src, crop)
    
    def do_apply_crop_imagemagick(self, msg: bytes, src: Image, crop: Transformation) -> Image:
        return self.do_apply_crop_pil(msg, src, crop)

    def do_extract(self, img: Image, transformation) -> bytes:
        if len(img.mode) != len(self.palette):
            debug(f'Invalid channel mode {img.mode} and palette config {self.palette}')
            return b''
        bits = []
        for _y in range(img.size[1]):
            for _x in range(img.size[0]):
                x, y = self.pixel_loc_mapper(_x, _y)
                _pixel = img.getpixel((x, y))
                for chnl in self.palette:
                    bits.append(_pixel[chnl] & ((1 << self.bits) - 1))
        bits = ''.join([bin(i)[2:].zfill(self.bits) for i in bits])
        while len(bits) % 8 != 0:
            bits += '0'
        bits_ = bits
        for i in range(1, 8):
            bits += i * '0' + bits_
        msg = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
        return bytes(msg)