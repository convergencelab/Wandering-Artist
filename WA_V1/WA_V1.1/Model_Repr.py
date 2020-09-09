import numpy as np
import json
import matplotlib.pyplot as plt
import os

# how many degrees turned per ms
TURN_DEG_PER_MS = 10
# speed of robot, 20ms/inch
VELOCITY_I_PER_MS = 0.05

OUTPUT_DIR = "../data/"


class Model_Repr():
    def __init__(self):
        # store the point on the plane and reference image
        # reference image will be str path to image in data
        # dict used to prevent reuse of same position
        self._points_on_plane = {}
        # start reference point at 0, 0 with direction of 0
        self._ref_point = (0, 0, 0)


    def log_new_point(self, TurnTimeRef, TravelTimeRef, UltraSoundRef, Forwards, frame=None):
        """
        turn_time: time spent turning
        time travelled: time spent moving
        forwards: bool, if True, move forwards, if false, moving backwards!
        to ensure simplicity in storing model, round all values to ints.
        frame: if frame = none, then this was not a position of which an image was snapped
        """
        x, y, angle = self._ref_point
        # Distance = time * velocity
        # the time will carry sign, negative sign represents distance travelled backwards
        distance = (TravelTimeRef * VELOCITY_I_PER_MS) + UltraSoundRef
        turn_angle = TurnTimeRef * TURN_DEG_PER_MS

        """ 
            using basic trig:
            x = Hcos(theta)
            y = Hsin(theta)
            ** May be wrong?? ***
        """
        # if time spent turning is positive: means in positive direction
        # compute angle
        if TurnTimeRef > 0:
            angle_prime = int((angle + turn_angle) % 360)
        else:
            angle_prime = int((angle + (turn_angle + 360))% 360)
        if Forwards:
            # compute trajectory
            x_prime = int(x + (distance * np.cos(angle_prime)))
            y_prime = int(y + (distance * np.sin(angle_prime)))
        else:
            x_prime = int(x - (distance * np.cos(angle_prime)))
            y_prime = int(y - (distance * np.sin(angle_prime)))

        # save ref x, y, angle
        self._ref_point = x_prime, y_prime, angle_prime
        # add new points to plane
        self._points_on_plane[x_prime, y_prime, angle_prime] = frame

    def log_location_ref(self, loc_ref, frame):
        """
        logs entire location reference array from arduino

        only one frame per ref, but potentially multiple steps leading up to it
        """
        # must be a multiple of 4
        assert len(loc_ref) % 4 == 0
        # index by 4
        for i in range(0, len(loc_ref)-4, 4):
            # initial steps will not have a image associated with it
            TurnTimeRef, TravelTimeRef, UltraSoundRef, Forwards = loc_ref[i:i+4]
            self.log_new_point(TurnTimeRef, TravelTimeRef, UltraSoundRef, Forwards)

        # last point will include the image
        TurnTimeRef, TravelTimeRef, UltraSoundRef, Forwards = loc_ref[len(loc_ref)-4:len(loc_ref)]
        self.log_new_point(TurnTimeRef, TravelTimeRef, UltraSoundRef, Forwards, frame)


    def save_model(self, fpath):
        """
        overwrites entire file with updated representation
        """
        with open(fpath, 'w') as outfile:
           json.dump(self._points_on_plane, outfile)

    def plot_model_space(self):
        plt.figure(figsize=(12, 16))
        points = [(x_prime, y_prime) for x_prime, y_prime, _ in self._points_on_plane.keys()]
        plt.plot(points)
        plt.show()

    def remove_point(self, point):
        # remove img
        img_location = self._points_on_plane[point]
        os.remove(img_location)
        # remove from model
        del self._points_on_plane[point]