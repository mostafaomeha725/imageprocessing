import streamlit as st
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Edge Detection", layout="wide")

if "page_navigation" not in st.session_state:
    st.session_state.page_navigation = "Edge Detection"

page = st.radio("Select a page:", ["Edge Detection", "Method Comparison"], key="page_navigation", index=0)

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

def clahe_equalization(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)

def gaussian_denoising(img): return cv2.GaussianBlur(img, (5, 5), 0)
def median_denoising(img): return cv2.medianBlur(img, 5)

def color_correction(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

def apply_extra_effect(img, effect):
    if effect in ["Color Correction", "Contrast Stretch"] and len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    if effect == "CLAHE Equalization":
        return clahe_equalization(img)
    elif effect == "Gaussian Denoising" or effect == "Gaussian Blur":
        return cv2.GaussianBlur(img, (5, 5), 0)
    elif effect == "Median Denoising":
        return median_denoising(img)
    elif effect == "Sharpening":
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        return cv2.filter2D(img, -1, kernel)
    elif effect == "Color Correction":
        return color_correction(img)
    elif effect == "Contrast Stretch":
        if len(img.shape) == 2:
            in_min = np.percentile(img, 2)
            in_max = np.percentile(img, 98)
            out = np.clip((img - in_min) * 255.0 / (in_max - in_min), 0, 255)
            return out.astype(np.uint8)
        else:
            out = img.copy()
            for c in range(3):
                in_min = np.percentile(img[:, :, c], 2)
                in_max = np.percentile(img[:, :, c], 98)
                out[:, :, c] = np.clip((img[:, :, c] - in_min) * 255.0 / (in_max - in_min), 0, 255)
            return out.astype(np.uint8)
    elif effect == "Thresholding":
        gray = img if len(img.shape) == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, th = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return th
    elif effect == "Invert":
        return cv2.bitwise_not(img)
    return img

methods = [
    "None", "Equalization", "Canny", "Sobel", "Sobel X", "Sobel Y", "Laplacian", "Prewitt", "Roberts"
]
extra_effects = [
    "None", "Gaussian Blur", "Sharpening", "Contrast Stretch", "Thresholding", "Invert",
    "CLAHE Equalization", "Gaussian Denoising", "Median Denoising", "Color Correction"
]

edge_map = {
    "Canny": lambda img, l=100, h=200: canny(img, l, h),
    "Sobel": sobel,
    "Sobel X": sobel_x,
    "Sobel Y": sobel_y,
    "Laplacian": laplacian,
    "Prewitt": prewitt,
    "Roberts": roberts
}

if page == "Edge Detection":
    with st.container():
        st.markdown("""
            <div style='border: 1px solid #888; border-radius: 10px; padding: 10px; background-color: #222;'>
                <h4 style='text-align: center; color: #fff;'>Image Edge Detection Techniques 🖼️</h4>
            </div>
        """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)

        target_width = 400
        aspect_ratio = img_array.shape[1] / img_array.shape[0]
        target_height = int(target_width / aspect_ratio)
        resized = cv2.resize(img_array, (target_width, target_height))
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

        st.markdown("#### Settings 🎛️")
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
            st.markdown("##### Original Image 📷")
            st.image(resized, width=400)

        with col_right:
            st.markdown(f"##### {selected_method} Result 🧪")

            if selected_method == "None":
                base_img = gray if selected_effect in ["CLAHE Equalization", "Gaussian Denoising", "Median Denoising"] else resized
                result = apply_extra_effect(base_img, selected_effect)
            elif selected_method == "Equalization":
                eq = equalize_image(gray)
                result = apply_extra_effect(eq, selected_effect)
                plot_histogram(result, "Image Histogram")
            else:
                edges = edge_map[selected_method](gray) if selected_method != "Canny" else canny(gray, low, high)
                result = apply_extra_effect(edges, selected_effect)

            st.image(result, width=400, clamp=True)

        scores = {}
        for method in edge_map:
            edges = edge_map[method](gray) if method != "Canny" else edge_map[method](gray, low, high)
            non_zero = np.count_nonzero(edges)
            scores[method] = non_zero
        st.session_state.scores = scores

elif page == "Method Comparison":
    scores = st.session_state.get("scores", {})

    if scores:
        st.markdown("### 🤖 Model Evaluation: Best Edge Detection Method")

        df = pd.DataFrame(list(scores.items()), columns=["Method", "Edge Pixels"])
        st.dataframe(df.sort_values(by="Edge Pixels", ascending=False), use_container_width=True)

        st.markdown("### 📊 Edge Detection Method Comparison")
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(scores.keys(), scores.values(), color='skyblue')
        ax.set_ylabel("Number of Edge Pixels")
        ax.set_title("Edge Detection Method Effectiveness")
        st.pyplot(fig)

        best_method = max(scores, key=scores.get)
        st.success(f"✅ The best method based on edge pixel count is: **{best_method}**")
    else:
        st.warning("⚠️ Please upload and process an image in the 'Edge Detection' page first.")
