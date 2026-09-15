"""
Sanity test: loads a pretrained YOLO model and runs detection
on a single frame from our test video.
"""

import cv2
from ultralytics import YOLO

# "yolov8n.pt" = YOLOv8 "nano" - the smallest, fastest version.
# Good for testing and for weaker machines; less accurate than
# larger versions, but a good starting point.
# This will auto-download the model file the first time it runs.
model = YOLO("yolov8n.pt")

# Grab a single frame from our test video to test on.
cap = cv2.VideoCapture("videos/test.mp4")
ret, frame = cap.read()
cap.release()

if not ret:
    print("ERROR: Could not read a frame from videos/test.mp4")
    exit(1)

print("Frame captured. Running detection...")

# Run YOLO detection on this one frame.
results = model(frame)

# results is a list (one entry per image we passed in - we passed one).
result = results[0]

print(f"\nDetected {len(result.boxes)} object(s):\n")

for box in result.boxes:
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    x1, y1, x2, y2 = box.xyxy[0].tolist()

    print(f"- {class_name} (confidence: {confidence:.2f}) at [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")

# Save an image showing the detections drawn on the frame, so we can see it visually.
annotated_frame = result.plot()
cv2.imwrite("test_detection_output.jpg", annotated_frame)
print("\nSaved visual result to test_detection_output.jpg")