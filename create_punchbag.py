"""
Create a simple punching bag image asset
"""
import cv2
import numpy as np

# Create a 200x200 transparent image
size = 200
img = np.zeros((size, size, 4), dtype=np.uint8)

# Draw punching bag shape
center_x, center_y = size // 2, size // 2

# Top hook
cv2.circle(img, (center_x, 20), 8, (128, 128, 128, 255), -1)
cv2.line(img, (center_x, 20), (center_x, 40), (128, 128, 128, 255), 4)

# Main bag body (pear shape)
# Upper part (narrower)
cv2.ellipse(img, (center_x, 80), (30, 35), 0, 0, 360, (220, 80, 80, 255), -1)
cv2.ellipse(img, (center_x, 80), (30, 35), 0, 0, 360, (180, 60, 60, 255), 2)

# Middle part
cv2.ellipse(img, (center_x, 115), (40, 40), 0, 0, 360, (220, 80, 80, 255), -1)
cv2.ellipse(img, (center_x, 115), (40, 40), 0, 0, 360, (180, 60, 60, 255), 2)

# Lower part (wider - pear shape)
cv2.ellipse(img, (center_x, 155), (45, 45), 0, 0, 360, (220, 80, 80, 255), -1)
cv2.ellipse(img, (center_x, 155), (45, 45), 0, 0, 360, (180, 60, 60, 255), 2)

# Center seam lines
cv2.line(img, (center_x, 60), (center_x, 180), (180, 60, 60, 255), 3)

# Horizontal stitching
for y in [90, 125, 160]:
    cv2.ellipse(img, (center_x, y), (35, 5), 0, 0, 360, (180, 60, 60, 255), 2)

# Highlight (shine effect)
cv2.ellipse(img, (center_x - 15, 100), (12, 25), -20, 0, 180, (255, 150, 150, 180), -1)

# Save
output_path = "assets/image/punching-bag.png"
cv2.imwrite(output_path, img)
print(f"Punching bag image created at: {output_path}")
