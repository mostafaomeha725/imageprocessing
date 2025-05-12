import cv2
import numpy as np
from PIL import Image
import io

def equalize_image(img):
    return cv2.equalizeHist(img)

def canny(img, low, high):
    return cv2.Canny(img, low, high)

def sobel(img):
    x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    y = cv2.Sobel(img, cv2.CV_64F, 0, 1)
    return np.uint8(cv2.magnitude(x, y))

def laplacian(img):
    return np.uint8(np.absolute(cv2.Laplacian(img, cv2.CV_64F)))

def prewitt(img):
    kx = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])
    ky = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
    return cv2.addWeighted(cv2.filter2D(img,-1,kx),0.5,cv2.filter2D(img,-1,ky),0.5,0)

def roberts(img):
    kx = np.array([[1,0],[0,-1]])
    ky = np.array([[0,1],[-1,0]])
    return cv2.addWeighted(cv2.filter2D(img,-1,kx),0.5,cv2.filter2D(img,-1,ky),0.5,0)


def process_image(file_bytes, method, low=100, high=200):
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img_array = np.array(image)

    target_width = 400
    aspect_ratio = img_array.shape[1] / img_array.shape[0]
    target_height = int(target_width / aspect_ratio)
    resized = cv2.resize(img_array, (target_width, target_height))
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

    if method == "Equalization":
        result = equalize_image(gray)
    else:
        edge_map = {
            "Canny": lambda img: canny(img, low, high),
            "Sobel": sobel,
            "Laplacian": laplacian,
            "Prewitt": prewitt,
            "Roberts": roberts
        }
        result = edge_map[method](gray)

    return result
