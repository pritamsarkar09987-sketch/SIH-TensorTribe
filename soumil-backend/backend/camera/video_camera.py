import cv2

VIDEO_PATH = "videos/test.mp4"

camera = cv2.VideoCapture(VIDEO_PATH)

if not camera.isOpened():
    print("Could not open video")
    exit()

print("Simulated CCTV started")
print("Press Q to stop")

while True:
    success, frame = camera.read()

    if not success:
        print("Video ended")
        break

    cv2.imshow("Simulated CCTV", frame)

    if cv2.waitKey(30) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()