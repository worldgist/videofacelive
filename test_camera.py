#!/usr/bin/env python3
"""Quick test: open camera 0 and show a window. Press any key to quit."""
import cv2
import sys

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open camera 0. Check Privacy & Security → Camera for this app.")
    sys.exit(1)

print("Camera opened. You should see a window. Press any key in the window to quit.")
cv2.namedWindow("Camera test", cv2.WINDOW_GUI_NORMAL)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Camera test", frame)
    if cv2.waitKey(1) >= 0:
        break
cap.release()
cv2.destroyAllWindows()
print("Done.")
