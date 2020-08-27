import os, sys
import tensorflow as tf
# object detection parent dir
research_dir = os.path.abspath("./models/research")
sys.path.append(research_dir)  # To find local version of the library
from object_detection.utils import visualization_utils as viz_utils
from tfzoo_utils import predict_obj, get_keypoint_tuples, get_model_detection_function
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.builders import model_builder
import cv2
import matplotlib.pyplot as plt
import serial, time


####################
# Object Detection #
####################
Experiment_title = "Prototype"
# coco dataset labels
label_map_path = "./models/research/object_detection/data/mscoco_label_map.pbtxt"
label_map = label_map_util.load_labelmap(label_map_path)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=label_map_util.get_max_label_map_index(label_map),
    use_display_name=True)
category_index = label_map_util.create_category_index(categories)
label_map_dict = label_map_util.get_label_map_dict(label_map, use_display_name=True)

## config pipeline ##
MODELS = {'centernet_with_keypoints': 'centernet_hourglass104_512x512_kpts_coco17_tpu-32',
          'centernet_without_keypoints': 'centernet_hourglass104_512x512_coco17_tpu-8',
          'ssd_efficientdet':'ssd_efficientdet_d0_512x512_coco17_tpu-8',
          'resnet-50-OO_kpts':'centernet_resnet50_v1_fpn_512x512_kpts_coco17_tpu-8'}

model_display_name = 'centernet_without_keypoints' # @param ['centernet_with_keypoints', 'centernet_without_keypoints']
model_name = MODELS[model_display_name]

pipeline_config = os.path.join('./models/research/object_detection/configs/tf2/',
                                model_name + '.config')
model_dir = './models/research/object_detection/test_data/' + model_name + '/checkpoint/'
# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(pipeline_config)
model_config = configs['model']

detection_model = model_builder.build(model_config=model_config, is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(
      model=detection_model)
ckpt.restore(os.path.join(model_dir, 'ckpt-0')).expect_partial()
detect_fn = get_model_detection_function(detection_model)

## Video Stream ##
# intialize connection with video stream
url = 'http://192.168.2.122:8080/video'
cap = cv2.VideoCapture(url)

# video writer to record outcome
width, height = (480, 480)
FPS = 24

fourcc = cv2.VideoWriter_fourcc(*'MP42')
video = cv2.VideoWriter('./{}.avi'.format(Experiment_title), fourcc, float(FPS), (width, height))

## Connect Arduino ##
arduino = serial.Serial('COM8', 115200, timeout=.1)
flag_descriptions = {
    0:"No Obstruction",
    1:"Obstruction"
}

while(True):
    ret, frame = cap.read()
    # listen for arduino
    time.sleep(1)
    flag = arduino.readline()[:-2]
    if flag:
        # right now any flag is considered obj detection
        try:
            isPotentialOBJ = int(flag)
        except:
            isPotentialOBJ = 0
    else:
        isPotentialOBJ = 0

    arduino.flush()
    print(flag_descriptions[isPotentialOBJ])

    # if not suspecting object show frame
    if frame is not None:
        if isPotentialOBJ:
            # run prediction on obj
            detections, predictions_dict, shapes = predict_obj(frame)
            # copy frame
            label_id_offset = 1
            image_np_with_detections = frame.copy()

            # Use keypoints if available in detections
            keypoints, keypoint_scores = None, None
            if 'detection_keypoints' in detections:
                keypoints = detections['detection_keypoints'][0].numpy()
                keypoint_scores = detections['detection_keypoint_scores'][0].numpy()

            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections['detection_boxes'][0].numpy(),
                (detections['detection_classes'][0].numpy() + label_id_offset).astype(int),
                detections['detection_scores'][0].numpy(),
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=200,
                min_score_thresh=.30,
                agnostic_mode=False,
                keypoints=keypoints,
                keypoint_scores=keypoint_scores,
                keypoint_edges=get_keypoint_tuples(configs['eval_config']))

            plt.figure(figsize=(12, 16))
            cv2.imshow(image_np_with_detections)
            video.write(image_np_with_detections)
            # write 1 to indicate sucessful obj detection
            arduino.write(b"1")
        else:
            cv2.imshow('frame', frame)
            video.write(frame)
            arduino.write(b"0")

    q = cv2.waitKey(1)
    if q == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
# plt.savefig("./test.png")