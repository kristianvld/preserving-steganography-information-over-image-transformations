from PIL import Image, ImageOps
import pywt
from transformations.transformation import Transformation
from .method import Method
import numpy as np
import qrcode
import pyzxing
import subprocess

# Fix libzbar.so.0 import bug on some linux distros
import ctypes, ctypes.util
ctypes.cdll.LoadLibrary(ctypes.util._findLib_ld('zbar'))

from pyzbar import pyzbar
import deqr

class ImprovedBarcodeReader(pyzxing.BarCodeReader):

    def __init__(self):
        super().__init__()
        self.extra_args = []
    
    def auto_decode(self, file):
        out = []
        self.extra_args = []
        out += self.decode(file)
        self.extra_args = ['--pure_barcode']
        out += self.decode(file)
        return out

    """
    Copy-pasted from pyzxing.BarCodeReader to allow extra CLI args, like --pure_barcode
    """
    def _decode(self, filename):
        cmd = ['zxing', filename, '--multi', '--try_harder', '--possibleFormats=QR_CODE', *self.extra_args]
        stdout = subprocess.check_output(cmd)
        lines = stdout.splitlines()
        separator_idx = [i for i in range(len(lines)) if lines[i].startswith(b'file')] + [len(lines)]

        result = [self._parse_single(lines[separator_idx[i]:separator_idx[i + 1]]) for i in range(len(separator_idx) - 1)]
        return result


def dwt2(gray_img, n=3):
    coeffs = [(gray_img, ())]
    for i in range(n):
        coeffs.append(list(pywt.dwt2(coeffs[i][0], 'haar')))
    return coeffs[1:]

def idwt2(coeffs):
    img = None
    while len(coeffs):
        img = pywt.idwt2(coeffs.pop(), 'haar')
        if len(coeffs):
            if coeffs[-1][1][0] is not None:
                coeffs[-1][0] = img[:coeffs[-1][1][0].shape[0], :coeffs[-1][1][0].shape[1]]
            else:
                coeffs[-1][0] = img
    return img

def fit_qr(img, target, flush=True):
    canvas = Image.new('L', target, color=255)
    size = min(target)
    img = img.resize((size, size), Image.NEAREST)
    pad = (0, 0) if flush else (abs(img.size[0] - target[0]) // 2, abs(img.size[1] - target[1]) // 2)
    canvas.paste(img, pad)
    return canvas.convert('RGB')

class DWT_Normal(Method):

    def __init__(self) -> None:
        self.origin_rate = 0.999
        self.secret_rate = 0.00215

    def dwt(self, msg: bytes, src: Image, repeat=1) -> Image:
        self.cover = src
        qr = qrcode.make(msg, border=1)
        qr = np.array(qr)
        qr = np.concatenate([qr] * repeat, axis=0)
        qr = np.concatenate([qr] * repeat, axis=1)
        qr = Image.fromarray(qr)
        qr = fit_qr(qr, src.size, repeat == 1)
        qr.save('outputs/qr.png')
        rgb = []
        for channel in src.mode:
            gray = src.getchannel(channel)
            coeffs = dwt2(gray)
            LL3 = coeffs[-1][0]

            secret = dwt2(np.array(qr.getchannel(channel)))[-1][0]

            LL3 = LL3 * self.origin_rate + secret * self.secret_rate

            coeffs[-1][0] = LL3
            gray2 = idwt2(coeffs)

            rgb.append(gray2)

        img_out = Image.fromarray(np.array(rgb).transpose((1,2,0)).astype(np.uint8))

        if src.height != img_out.height or src.width != img_out.width:
            # some times our returned image might be off-size by one or two pixels in height/width, 
            # we paste into the original to just keep those rows/columns as is from the original
            img_ = src.copy()
            img_.paste(img_out, (0,0))
            img_out = img_


        return img_out

    def do_apply_none(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)
    
    def do_apply_crop_pil(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src, repeat=3)

    def do_apply_crop_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src, repeat=3)

    def do_apply_downscale_pil_normal(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_downscale_pil_fast(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_downscale_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_convert_2jpg_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_convert_2jpg_pil(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_convert_2png_imagemagick(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def do_apply_convert_2png_pil(self, msg: bytes, src: Image, transformation: Transformation) -> Image:
        return self.dwt(msg, src)

    def try_extract(self, img, file, transform) -> bytes:
        if 'crop' not in transform.__class__.__name__.lower():
            size = min(img.size)
            img = img.crop((0,0,size,size))
        img.save(file)
        msg = b''
        for data in pyzbar.decode(img):
            msg += data.data
        reader = ImprovedBarcodeReader()
        for data in reader.auto_decode(file):
            if 'raw' in data:
                msg += data['raw']
        for hit in deqr.QRdecDecoder().decode(img):
            for data in hit.data_entries:
                msg += data.data.encode()
        return msg

    def do_extract(self, img: Image, transformation: Transformation) -> bytes:
        rgb = []
        msg = b''
        if img.size != self.cover.size:
            path = self.cover._dump()
            self.cover = Image.open(transformation.apply(path, path + '.' + img.format))
        for channel in img.mode:
            gray = img.getchannel(channel)
            coeffs = dwt2(gray)
            LL3 = coeffs[-1][0]

            cover = dwt2(self.cover.getchannel(channel))[-1][0]

            secret = LL3 - (cover * self.origin_rate)
            secret = secret / self.secret_rate

            coeffs[-1][0] = secret
            gray2 = secret
            coeffs2 = [([secret, (None, None, None)]) for _ in range(len(coeffs))]
            
            gray2 = idwt2(coeffs2)
            gray2 = gray2.clip(0, 255)
            rgb.append(gray2)

            msg += self.try_extract(Image.fromarray(gray2.astype(np.uint8)), f'outputs/qr-extracted-{channel}.png', transformation)


        rgb_image = Image.fromarray(np.array(rgb).transpose((1,2,0)).astype(np.uint8))
        msg += self.try_extract(rgb_image, 'outputs/qr-extracted-RGB-Normal.png', transformation)
        msg += self.try_extract(rgb_image.convert('L'), 'outputs/qr-extracted-L.png', transformation)
        
        # Assemble r g & b and try to normalize the image
        gray = rgb[0] + rgb[1] + rgb[2]
        for ratio in [0.001, 0.1, 0.25, 0.5, 0.666, 0.75, 1, 1.25, 1.5, 1.75, 1.9, 1.99]:
            gray2 = (gray > int(np.median(gray) * ratio)) * 255
            gray2 = gray2.clip(0, 255).astype(np.uint8)
        
            msg += self.try_extract(Image.fromarray(gray2), f'outputs/qr-extracted-RGB-{ratio}.png', transformation)
        
        return msg        
