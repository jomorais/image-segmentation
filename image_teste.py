import cv2
import time

cap = cv2.VideoCapture(0)
ret = cap.set(3, 320)
ret = cap.set(4, 240)

while(True):
    inicio_captura = time.time()
    ret, frame = cap.read()
    fim_captura = time.time()

    inicio_mostra = time.time()
    cv2.imshow('teste', frame)
    fim_mostra = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print 'tempo captura: ' + str(fim_captura - inicio_captura) + ', tempo mostra: ' + str(fim_mostra - inicio_mostra)