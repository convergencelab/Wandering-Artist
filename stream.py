import cv2

url = 'http://192.168.2.122:8080/video'
cap = cv2.VideoCapture(url)

while True:
    _, img = cap.read()
    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    # escape key
    if key==27:
        break

cap.release()
cv2.destroyAllWindows()