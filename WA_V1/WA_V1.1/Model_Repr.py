import numpy as np
import json
import matplotlib.pyplot as plt

# how many degrees turned per ms
TURN_DEG_PER_MS = 10
# speed of robot, meters per ms
VELOCITY_M_PER_MS = 0.1


class Model_Repr():
    def __init__(self):
        # store the point on the plane and reference image
        # reference image will be str path to image in data
        # dict used to prevent reuse of same position
        self._points_on_plane = {}
        # start reference point at 0, 0 with direction of 0
        self._ref_point = (0, 0, 0)


    def log_new_point(self, turn_time, time_travelled, forwards, frame):
        """
        turn_time: time spent turning
        time travelled: time spent moving
        forwards: bool, if True, move forwards, if false, moving backwards!
        to ensure simplicity in storing model, round all values to ints.
        """
        x, y, angle = self._ref_point
        # Distance = time * velocity
        distance = time_travelled * VELOCITY_M_PER_MS
        turn_angle = turn_time * TURN_DEG_PER_MS
        angle_prime = int(abs((angle + turn_angle) % 360))
        """ 
            using basic trig:
            x = Hcos(theta)
            y = Hsin(theta)
        """
        if forwards:
            x_prime = int(x + (distance * np.cos(angle_prime)))
            y_prime = int(y + (distance * np.sin(angle_prime)))
        else:
            x_prime = int(x - (distance * np.cos(angle_prime)))
            y_prime = int(y - (distance * np.sin(angle_prime)))

        # save ref x, y, angle
        self._ref_point = x_prime, y_prime, angle_prime
        # add new points to plane
        self._points_on_plane[x_prime, y_prime, angle_prime] = frame

    def save_model(self, fpath):
        """
        overwrites entire file with updated representation
        """
        with open(fpath, 'w') as outfile:
           json.dump(self._points_on_plane, outfile)

    def plot_model_space(self):
        plt.figure(figsize=(12, 16))
        points = [(x_prime, y_prime) for x_prime, y_prime, _ in self._points_on_plane.keys()]
        plt.scatter(points)
        plt.show()


