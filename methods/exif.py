from PIL.ExifTags import TAGS
from PIL import Image
from transformations.transformation import Transformation
from transformations.none_transform import NoneTransformation
from .method import Method

# When Pillow saves images, it only export exif tags on .png images, regardless of input format.
# Pillow supports reading exif tags for both .jpg and .png images
PIL_PNG = ['Make', 'Software', 'Artist', 'Copyright']
TAGS_REV = {v: k for k, v in TAGS.items()}
PIL_PNG_TAGS = [TAGS_REV[name] for name in PIL_PNG if name in TAGS_REV]

class Exif(Method):

    """
    tag_name, which exif metadata tag to embedd the message in
    """
    def __init__(self, tag_name='Artist') -> None:
        self.tag_name = tag_name
        # Find Pillow EXIF tag id from name
        for id, name in TAGS.items():
            if name == tag_name:
                self.tag_id = id
    
    def apply_pil(self, msg: bytes, src: str, dst: str) -> None:
        img = Image.open(src)
        exif = img.getexif()
        tags = {tag: msg.decode() for tag in PIL_PNG_TAGS}
        exif.update(tags)
        img.save(dst, exif=exif)
    
    def do_apply_none_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_downscale_pil_normal_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_downscale_pil_fast_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)
    
    def do_apply_crop_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)
    
    def do_apply_convert_2jpg_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_convert_2png_pil_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)
    
    def do_apply_downscale_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_crop_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_convert_2jpg_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_apply_convert_2png_imagemagick_raw(self, msg: bytes, src: str, dst: str, transformation: Transformation) -> None:
        self.apply_pil(msg, src, dst)

    def do_extract(self, img: Image, transformation: Transformation) -> bytes:
        exif = img.getexif()
        for tag in PIL_PNG_TAGS:
            value = exif.get(tag, '')
            if value:
                return value.encode()
        return b''