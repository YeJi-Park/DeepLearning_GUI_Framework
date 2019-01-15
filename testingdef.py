
import tensorflow as tf
import sys
import os
import numpy as np
from PIL import Image

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def findButton(image_path):
    image = Image.open(image_path)
    image_np = load_image_into_numpy_array(image)
    image_np_ex = np.expand_dims(image_np, axis=0)

    MODEL_PATH = "output_graph/"

    graph_def = tf.train.import_meta_graph(os.path.join(MODEL_PATH, "model.ckpt.meta"))
    tf.reset_default_graph()

    with tf.Session() as sess:
        new_graph_def = tf.train.import_meta_graph(os.path.join(MODEL_PATH, "model.ckpt.meta"))
        new_graph_def.restore(sess, tf.train.latest_checkpoint(MODEL_PATH))

        d_boxes = sess.graph.get_tensor_by_name("detection_boxes:0")
        d_scores = sess.graph.get_tensor_by_name("detection_scores:0")
        d_classes = sess.graph.get_tensor_by_name("detection_classes:0")
        num_d = sess.graph.get_tensor_by_name("num_detections:0")
        image_tensor = sess.graph.get_tensor_by_name("image_tensor:0")

        (boxes, scores, classes, num) = sess.run([d_boxes, d_scores, d_classes, num_d],
                                                 feed_dict={image_tensor: image_np_ex})

        sq_box = np.squeeze(boxes)
        sq_classes = np.squeeze(classes).astype(np.int32)
        sq_scores = np.squeeze(scores)
        sq_num = np.squeeze(num).astype(np.int32)

        n_obj = 0
        detection_dict = [0]

        for i in range(sq_num):
            if sq_scores[i] > 0.5:
                # y_coor = (sq_box[i][0] + sq_box[i][2]) / 2
                # x_coor = (sq_box[i][1] + sq_box[i][3]) / 2

                y1 = sq_box[i][0];
                x1 = sq_box[i][1];
                y2 = sq_box[i][2];
                x2 = sq_box[i][3];

                detection_dict.append([sq_classes[i], x1, y2, x2, y1])
            else:
                n_obj = i
                break

        del detection_dict[0]

    for i in range(len(detection_dict)):
        detection_dict.sort(key=lambda x: x[2])

    return detection_dict