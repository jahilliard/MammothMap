import numpy as np
import time
import tkinter
import requests
import PIL.Image, PIL.ImageTk
import cv2
import os
import xml.etree.ElementTree as ET  


class MammothMap(tkinter.Tk):
    lift_map = {
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

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.canvas = tkinter.Canvas(self, width = screen_width, height = screen_height)
        self.canvas.pack()
        self.place_image()

    def get_lift_information(self):
        curr_lift_state = []
        lift_status = requests.get('https://rp.trailtap.com/api/getMapDetails/mammoth?mapID=', 
                headers = {'User-Agent':'Mammoth/5.15.1 CFNetwork/975.0.3 Darwin/18.2.0'})
        xml_blob = ET.fromstring(lift_status.text)
        for lift in xml_blob.iter('lift'):
            if lift.attrib['heading'] != 'Village Gondola':
                curr_lift = lift.attrib
                curr_lift['filename'] = self.lift_map[lift.attrib['heading']]
                curr_lift_state.append(curr_lift)
        return(curr_lift_state)
    
    def load_image(self):
        print('reloaded image')
        image = cv2.imread('mammothMountain.png')
        curr_lift_state = self.get_lift_information()
        path = os.path.dirname(os.path.abspath(__file__)) + '/lifts/'
        for lift in curr_lift_state:
            curr_chair = cv2.imread(path+lift['filename'], -1)
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
        return(convert_image)
    
    def place_image(self):
        self.image = self.load_image()
        self.photo = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.image))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.after(2000, self.place_image) 

if __name__== "__main__":
    app = MammothMap()
    app.mainloop()

