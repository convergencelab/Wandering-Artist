import cv2
import numpy as np

comm = {
    0:"take photo"
}

net = cv2.dnn.readNet('yolov3-tiny.meta', 'yolov3-tiny.cfg')
classes = []
with open('meta/coco.names', 'r') as f:
    classes = f.read().splitlines()

url = 'http://192.168.2.122:8080/video'
cap = cv2.VideoCapture(url)


while True:
    _, img = cap.read()
    height, width, _ = img.shape
    # prepare img for model
    blob = cv2.dnn.blobFromImage(img, 1, (416, 416), (0,0,0), crop=False)
    net.setInput(blob)

    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)

                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    colours = np.random.uniform(0, 255, size=(len(boxes), 3))
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = colours[i]
            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y+20), font, 2, (255, 255, 255), 2)

    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    # escape key
    if key==27:
        break

cap.release()
cv2.destroyAllWindows()