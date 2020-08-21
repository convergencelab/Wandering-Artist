import matplotlib
import matplotlib.pyplot as plt
import os
import sys
import io
import scipy.misc
import numpy as np
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
# object detection parent dir
research_dir = os.path.abspath("./models/research")
sys.path.append(research_dir)  # To find local version of the library

def load_image_into_numpy_array(img):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
    path: the file path to the image

    Returns:
    uint8 numpy array with shape (img_height, img_width, 3)
    """
    img_data = tf.io.gfile.GFile(img, 'rb').read()
    image = Image.open(BytesIO(img_data)).resize(INPUT_SIZE)
    (im_width, im_height) = image.size
    arr = np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
    return arr


def get_keypoint_tuples(eval_config):
    """Return a tuple list of keypoint edges from the eval config.

    Args:
      eval_config: an eval config containing the keypoint edges

    Returns:
      a list of edge tuples, each in the format (start, end)
    """
    tuple_list = []
    kp_list = eval_config.keypoint_edge
    for edge in kp_list:
        tuple_list.append((edge.start, edge.end))
    return tuple_list


def get_model_detection_function(model):
  """Get a tf.function for detection."""

  @tf.function
  def detect_fn(image):
    """Detect objects in image."""

    image, shapes = model.preprocess(image)
    prediction_dict = model.predict(image, shapes)
    detections = model.postprocess(prediction_dict, shapes)

    return detections, prediction_dict, tf.reshape(shapes, [-1])

  return detect_fn


def predict_obj(image):
    if not isinstance(image, np.array):
        image = load_image_into_numpy_array(image)

    input_tensor = tf.convert_to_tensor(
        np.expand_dims(image, 0), dtype=tf.float32)
    detections, predictions_dict, shapes = detect_fn(input_tensor)

    return detections, predictions_dict, shapes

