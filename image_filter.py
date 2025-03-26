# image_filter.py

import cv2
import numpy as np
from sklearn.cluster import KMeans

def quantize_image(image, k=8):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10).fit(pixels)
    quantized_img = kmeans.cluster_centers_[kmeans.labels_].reshape(img_rgb.shape)
    return cv2.cvtColor(quantized_img.astype(np.uint8), cv2.COLOR_RGB2BGR)

def convert_to_colored_sketch(image_path, color_intensity=0.9, gamma=1.3, posterize_levels=16):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    bilateral_filtered = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    quantized = quantize_image(bilateral_filtered, k=posterize_levels)
    gray = cv2.cvtColor(quantized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 7)
    edges = cv2.Canny(bilateral_filtered, threshold1=50, threshold2=150)

    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.convertScaleAbs(edges, alpha=1.5, beta=0)
    sharp_edges = cv2.addWeighted(edges, 2, cv2.GaussianBlur(edges, (5,5), 0), -1, 0)

    edges_inv = cv2.bitwise_not(sharp_edges)
    edges_inv_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

    gray_colored = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    desaturated = cv2.addWeighted(quantized, color_intensity, gray_colored, 1 - color_intensity, 0)
    gamma_corrected = np.array(255 * (desaturated / 255) ** (1 / gamma), dtype=np.uint8)

    colored_sketch = cv2.bitwise_and(gamma_corrected, edges_inv_colored)
    return colored_sketch