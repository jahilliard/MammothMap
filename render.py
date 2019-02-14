import os
import cv2
import numpy as np
import PIL.Image, PIL.ImageTk
from checksum import Checksum

class Render(object):

    LIFT_MAP = {
        'Broadway Express 1': 'braodway.png',
        'Stump Alley Express 2': 'stump.png',
        'Face Lift Express 3': '3.png',
        'Roller Coaster Express 4': 'rollercoaster.png',
        'High 5 Express': '5.png',
        'Unbound Express 6': 'unbound6.png',
        'Chair 7': '7.png',
        'Chair 8': '8.png', 
        'Cloud Nine Express 9': '9.png',
        'Gold Rush Express 10': 'goldrush.png',
        'Discovery Express 11': 'discovery.png',
        'Chair 12': '12.png',
        'Chair 13': '13.png',
        'Chair 14': '14.png',
        'Eagle Express 15': 'eagle.png',
        'Canyon Express 16': 'canyon.png',
        'Schoolyard Express 17': '17.png',
        'Chair 20': '20.png',
        'Chair 21': '21.png',
        'Chair 22': '22.png',
        'Chair 23': '23.png',
        'Chair 25': '25.png',
        'Panorama Lower': 'lowergondi.png',
        'Panorama Upper': 'uppergondi.png'
    }

    cached_checksum = None
    cached_image = None

    def __init__(self, lift_status):
        self.lift_status = lift_status
        self.checksum = Checksum(lift_status).checksum()

    def render_and_etag(self):
        if self.checksum == Render.cached_checksum:
            return (Render.cached_image, Render.cached_checksum)
        return (self.render(), self.checksum)

    def render(self):
        if self.checksum == Render.cached_checksum:
            return Render.cached_image
        image = cv2.imread('assets/mammothMountain.png')
        curr_lift_state = self.lift_status
        path = os.path.dirname(os.path.abspath(__file__)) + '/assets/lifts/'
        for lift in curr_lift_state:
            curr_chair = cv2.imread(path+Render.LIFT_MAP[lift['heading']], -1)
            lower = np.array([0,0,0,200], dtype = "uint8")
            upper = np.array([2,2,2,255], dtype = "uint8")
            mask = cv2.inRange(curr_chair, lower, upper)
            if lift['status'] == 'OPEN':
                image[np.where(mask!=0)] = [20,255,57]
            elif lift['status'] == 'CLOSED':
                image[np.where(mask!=0)] = [91,23,248]
            else:
                image[np.where(mask!=0)] = [26,173,251]
        convert_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        Render.cached_image = convert_image 
        Render.cached_checksum = self.checksum
        return convert_image
