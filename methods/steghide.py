from PIL.ExifTags import TAGS
from PIL import Image
from transformations.transformation import Transformation
from transformations.none_transform import NoneTransformation
from .method import Method
from utils.logger import print, debug
import subprocess
import shutil
import os
import tempfile

class Steghide(Method):

    """
    steghide requires a passphrase for normal usage
    """
    def __init__(self, passphrase='Attack at Dawn') -> None:
        self.passphrase = passphrase

    def apply_pil(self, msg: bytes, src: str, dst: str) -> None:
        img = Image.open(src)
        exif = img.getexif()
        exif.update({self.tag_id: msg.decode()})
        img.save(dst, exif=exif)
    
    def apply_steghide_raw(self, msg: bytes, dst: str) -> None:
        proc = subprocess.Popen(['steghide', 'embed', '--coverfile', dst, '--embedfile', '-', '--passphrase', self.passphrase], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=msg)
        debug('stdout:', stdout)
        debug('stderr:', stderr)

    def apply_steghide_spoof(self, msg: bytes, dst: str, ending='bmp') -> None:
        img = Image.open(dst)
        tmp = tempfile.gettempdir() + '/steghide-tempfile.' + ending
        debug('Converting to tmp', tmp.encode())
        img.save(tmp)

        self.apply_steghide_raw(msg, tmp)

        img = Image.open(tmp)
        img.save(dst)
        debug('Converting back to target', dst.encode())
        os.remove(tmp)
    
    def apply_steghide_png(self, msg: bytes, dst: str) -> None:
        self.apply_steghide_spoof(msg, dst, ending='bmp')

    
    def apply_steghide_auto(self, msg: bytes, src: str, dst: str) -> None:
        shutil.copy(src, dst)
        if dst.lower().endswith('.png'):
            self.apply_steghide_png(msg, dst)
        else:
            self.apply_steghide_raw(msg, dst)
            

    def do_apply_none_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)
    
    def do_apply_downscale_pil_normal_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)

    def do_apply_downscale_pil_fast_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)
    
    def do_apply_downscale_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)

    def do_apply_crop_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)
    
    def do_apply_crop_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_steghide_auto(msg, src, dst)
    
    def do_apply_convert_2png_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        shutil.copy(src, dst)
        self.apply_steghide_spoof(msg, dst, ending='jpg')

    def do_apply_convert_2png_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        shutil.copy(src, dst)
        self.apply_steghide_spoof(msg, dst, ending='jpg')

    def do_apply_convert_2jpg_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        shutil.copy(src, dst)
        self.apply_steghide_spoof(msg, dst, ending='jpg')

    def do_apply_convert_2jpg_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        shutil.copy(src, dst)
        self.apply_steghide_spoof(msg, dst, ending='jpg')

    def extract_raw(self, dst: str) -> bytes:
        proc = subprocess.Popen(['steghide', 'extract', '--stegofile', dst, '--extractfile', '-', '--passphrase', self.passphrase], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        debug('stdout:', stdout)
        debug('stderr:', stderr)
        return stdout

    def extract_spoof(self, dst: str, ending) -> bytes:
        img = Image.open(dst)
        dst = tempfile.gettempdir() + '/steghide-tempfile.' + ending
        img.save(dst)
        out = self.extract_raw(dst)
        os.remove(dst)
        return out


    def extract(self, dst: str, transformation: Transformation) -> bytes:
        if 'convert' in transformation.__class__.__name__.lower():
            return self.extract_spoof(dst, 'jpg')

        if dst.lower().endswith('.png'):
            return self.extract_spoof(dst, 'bmp')
        
        return self.extract_raw(dst)