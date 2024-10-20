import cv2

cap = cv2.VideoCapture(0)  # デバイスIDを適切に設定

if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Press 'Ctrl + c' to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame. Exiting ...")
        break
    cv2.imshow('Camera Test', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()