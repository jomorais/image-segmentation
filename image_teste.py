import cv2

cap = cv2.VideoCapture(0)
ret = cap.set(3, 320)
ret = cap.set(4, 240)

while(True):
    ret, frame = cap.read()

    cv2.imshow('teste', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break