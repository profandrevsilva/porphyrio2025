import cv2
import numpy as np

# -----------------------------
# 1. Load the image as grayscale
img_path = "math_gabarito.png"
#img_path = "edf_cnt_gabarito.png"
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

# Convert to NumPy array (optional, img is already a NumPy array)
img_array = np.array(img)
print("Image shape:", img_array.shape)
print("Data type:", img_array.dtype)

# -----------------------------
# 2. Threshold the image to isolate black areas
_, thresh = cv2.threshold(img_array, 50, 255, cv2.THRESH_BINARY_INV)
# THRESH_BINARY_INV because black areas will become white

# Remove small noise
kernel = np.ones((3, 3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# -----------------------------
# 3. Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# -----------------------------
# 4. Filter contours to detect circles
circles = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 14:  # ignore tiny spots
        continue
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    if 0.7 < circularity <= 1.2:  # 1.0 is perfect circle
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius > 12:  # ignore tiny circles
            circles.append((int(x), int(y), int(radius)))

# -----------------------------
# 5. Print detected circles
print(f"Detected {len(circles)} black circles:")
for i, (x, y, r) in enumerate(circles, start=1):
    print(f"Circle {i}: Center=({x},{y}), Radius={r}")

# -----------------------------
# 6. Optional: visualize detected circles
img_color = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
for x, y, r in circles:
    cv2.circle(img_color, (x, y), r, (0, 0, 255), 2)

cv2.imshow("Detected Circles", img_color)
cv2.waitKey(0)
cv2.destroyAllWindows()
