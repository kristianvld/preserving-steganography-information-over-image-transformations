import math
import numpy as np
from PIL import Image
from .logger import print

# MSE, PSNR and NCC calculations followed by
# https://cvnote.ddlee.cc/2019/09/12/psnr-ssim-python


def mse(img1, img2):
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    return np.mean((arr1 - arr2)**2)

def psnr(img1, img2):
    _mse = mse(img1, img2)
    if _mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(_mse))

def normalize(arr):
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    return (arr - mean) / std

def ncc(img1, img2):
    arr1 = normalize(np.array(img1))
    arr2 = normalize(np.array(img2))
    return (1.0/(arr1.size - 1)) * np.sum(arr1 * arr2)

def diff(img1, img2, amplify=50):

    arr1 = np.array(img1)
    arr2 = np.array(img2)

    diff = abs(arr1 - arr2)

    diff_sum = diff.sum(axis=2)

    print('Sum diff:', diff.sum())
    print('Count pixels diff:', diff_sum.clip(0, 1).sum())
    print('Biggest diff:', diff_sum.max())

    if amplify:
        diff = (diff.astype(np.uint64) * amplify).clip(0, 255).astype(np.uint8)
    
    return Image.fromarray(diff), amplify
