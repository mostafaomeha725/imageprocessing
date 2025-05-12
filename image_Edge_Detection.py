import streamlit as st
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="Edge Detection", layout="wide")
with st.container():
    st.markdown("""
        <div style='border: 1px solid #888; border-radius: 10px; padding: 10px; background-color: #222;'>
            <h4 style='text-align: center; color: #fff;'>Image Edge Detection Techniques 🖼️</h4>
        </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

def plot_histogram(image, title="Histogram"):
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.hist(image.ravel(), bins=256, range=(0, 256), color='steelblue')
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Pixel Intensity", fontsize=8)
    ax.set_ylabel("Frequency", fontsize=8)
    ax.tick_params(axis='both', labelsize=7)
    st.pyplot(fig)

def equalize_image(img): return cv2.equalizeHist(img)
def canny(img, low, high): return cv2.Canny(img, low, high)
def sobel(img):
    x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
    y = cv2.Sobel(img, cv2.CV_64F, 0, 1)
    return np.uint8(cv2.magnitude(x, y))
def sobel_x(img): return np.uint8(np.absolute(cv2.Sobel(img, cv2.CV_64F, 1, 0)))
def sobel_y(img): return np.uint8(np.absolute(cv2.Sobel(img, cv2.CV_64F, 0, 1)))
def laplacian(img): return np.uint8(np.absolute(cv2.Laplacian(img, cv2.CV_64F)))
def prewitt(img):
    kx = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])
    ky = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
    return cv2.addWeighted(cv2.filter2D(img,-1,kx),0.5,cv2.filter2D(img,-1,ky),0.5,0)
def roberts(img):
    kx = np.array([[1,0],[0,-1]])
    ky = np.array([[0,1],[-1,0]])
    return cv2.addWeighted(cv2.filter2D(img,-1,kx),0.5,cv2.filter2D(img,-1,ky),0.5,0)

def apply_extra_effect(img, effect):
    if effect == "Gaussian Blur":
        return cv2.GaussianBlur(img, (5, 5), 0)
    elif effect == "Sharpening":
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        return cv2.filter2D(img, -1, kernel)
    elif effect == "Contrast Stretch":
        return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    elif effect == "Thresholding":
        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return thresh
    elif effect == "Invert":
        return cv2.bitwise_not(img)
    return img

methods = ["Equalization", "Canny", "Sobel", "Sobel X", "Sobel Y", "Laplacian", "Prewitt", "Roberts"]
extra_effects = ["None", "Gaussian Blur", "Sharpening", "Contrast Stretch", "Thresholding", "Invert"]

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    target_width = 400
    aspect_ratio = img_array.shape[1] / img_array.shape[0]
    target_height = int(target_width / aspect_ratio)
    resized = cv2.resize(img_array, (target_width, target_height))
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

    st.markdown("####  Settings 🎛️")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        low = st.slider("Low Threshold", 0, 255, 100)
    with col2:
        high = st.slider("High Threshold", 0, 255, 200)
    with col3:
        selected_method = st.selectbox("Choose Edge Detection Method", methods)

    selected_effect = st.selectbox("Extra Effect ✨ ", extra_effects)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("##### Original Image 📷 ")
        st.image(resized, width=400)

    with col_right:
        st.markdown(f"#####  {selected_method} Result 🧪")

        if selected_method == "Equalization":
            eq = equalize_image(gray)
            result = apply_extra_effect(eq, selected_effect)
            st.image(result, width=400, clamp=True)
            plot_histogram(result, "Image Histogram")
        else:
            edge_map = {
                "Canny": lambda img: canny(img, low, high),
                "Sobel": sobel,
                "Sobel X": sobel_x,
                "Sobel Y": sobel_y,
                "Laplacian": laplacian,
                "Prewitt": prewitt,
                "Roberts": roberts
            }
            edges = edge_map[selected_method](gray)
            result = apply_extra_effect(edges, selected_effect)
            st.image(result, width=400, clamp=True)

    st.markdown("<h4 style='text-align: center;'> Made By : Eng Mostafa Basiony 💻🤖 </h4>", unsafe_allow_html=True)
