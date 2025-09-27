from PIL import Image
import cv2
import easyocr
import numpy as np

img = cv2.imread("math_gabarito.png", cv2.IMREAD_GRAYSCALE)

# Threshold image to get black areas
_, thresh = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)  
# THRESH_BINARY_INV because black circles will become white

# Optional: remove small noise
kernel = np.ones((3,3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter for circular shapes
circles = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 10:  # ignore tiny spots
        continue
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue
    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    if 0.7 < circularity <= 1.2:  # 1.0 is a perfect circle
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius > 12:
            circles.append((int(x), int(y), int(radius)))

print(f"Detected {len(circles)} black circles:")
for c in circles:
    print(f"Center: ({c[0]}, {c[1]}), Radius: {c[2]}")

# Optional: draw detected circles
img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for x, y, r in circles:
    cv2.circle(img_color, (x, y), r, (0, 0, 255), 2)

cv2.imshow("Detected Circles", img_color)
cv2.waitKey(0)
cv2.destroyAllWindows()