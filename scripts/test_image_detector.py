#!/usr/bin/env python3
"""
Quick dev test for the LightweightImageDetector.
Generates synthetic images and runs the analyzer to spot-check false positives.

Usage:
  python scripts/test_image_detector.py
"""
import os
import sys
import pathlib
import tempfile
import json
import numpy as np
import cv2

# Ensure repository root is on sys.path for 'backend' package imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
for p in [ROOT, BACKEND]:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from backend.app.models.image_model import analyze_image


def create_clean_like_photo(path):
    # Create a synthetic "clean" photo-like image with gradients and noise
    h, w = 720, 1080
    x = np.linspace(0, 1, w)
    y = np.linspace(0, 1, h)
    xv, yv = np.meshgrid(x, y)

    # Smooth gradient background
    base = (0.3 + 0.7 * xv * (1 - yv))

    # Add mild texture/noise
    noise = np.random.normal(0, 0.02, (h, w))
    img = np.clip(base + noise, 0, 1)

    # Add some edges: draw a rectangle and lines
    img_color = (np.stack([img, img * 0.95, img * 1.05], axis=-1) * 255).astype(np.uint8)
    cv2.rectangle(img_color, (100, 100), (980, 620), (180, 180, 180), 3)
    cv2.line(img_color, (100, 360), (980, 360), (160, 160, 160), 2)
    cv2.line(img_color, (540, 100), (540, 620), (160, 160, 160), 2)

    cv2.imwrite(path, img_color, [int(cv2.IMWRITE_JPEG_QUALITY), 92])


def create_suspicious_flat_image(path):
    # Create an overly smooth, low-texture image
    h, w = 512, 512
    img_color = np.full((h, w, 3), 170, dtype=np.uint8)
    # Slight vignette to avoid total uniformity
    for i in range(h):
        for j in range(w):
            dist = ((i - h/2)**2 + (j - w/2)**2)**0.5
            factor = 1 - min(0.2, dist / (max(h, w)))
            img_color[i, j] = (img_color[i, j] * factor).astype(np.uint8)
    cv2.imwrite(path, img_color, [int(cv2.IMWRITE_JPEG_QUALITY), 85])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        clean_path = os.path.join(tmp, "clean.jpg")
        flat_path = os.path.join(tmp, "flat.jpg")

        create_clean_like_photo(clean_path)
        create_suspicious_flat_image(flat_path)

        clean_res = analyze_image(clean_path)
        flat_res = analyze_image(flat_path)

        print("Clean-like image result:")
        print(json.dumps(clean_res, indent=2))
        print("\nFlat/suspicious image result:")
        print(json.dumps(flat_res, indent=2))

        print("\nSummary:")
        print(f"Clean isDeepfake={clean_res['isDeepfake']}, confidence={clean_res['confidence']}")
        print(f"Flat isDeepfake={flat_res['isDeepfake']}, confidence={flat_res['confidence']}")


if __name__ == "__main__":
    main()
