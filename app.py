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

    # def log_lift_status(self, lift_xml):
    #     f=open("liftStatus.xml", "a+")
    #     f.write(lift_xml)

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
        self.place_weather()
        self.canvas.create_rectangle(1250, 700, 1750, 950, fill = "#ADD8E6")
        self.after(30000, self.place_image)

    def place_weather(self):
        self.weather = self.get_weather_information()
        self.canvas.create_text(1500, 720, text = '24 hour snow ' + self.weather['Snowfall24Hour'] + '\'')
        self.canvas.create_text(1500, 735, text = 'Tempurature is ' + self.weather['TempuratureF'])
        self.canvas.create_text(1500, 750, text = 'Current Conditions ' + self.weather['CurrentConditionName'])
        self.canvas.create_text(1500, 765, text = 'Current Surface ' + self.weather['Surface'])
        self.canvas.create_text(1500, 780, text = 'Current Summit Wind Speed ' + self.weather['WindDetails']['Summit']['Speed'])
        self.canvas.create_text(1500, 795, text = 'Current Summit Wind Direction ' + self.weather['WindDetails']['Summit']['Direction'])
        self.after(30000, self.place_weather)

    def make_weather_xml_path(self, *args):
        xmlns = '{http://schemas.mammothmountain.com/Weather/2.0}'
        built_path = './'
        for path in args:
            built_path = built_path + xmlns + path + '/'
        return(built_path[:-1])

    def get_weather_information(self):
        weather_txt = requests.get('https://rp.trailtap.com/api/getExtendedWeather/mammoth',
                    headers = {'User-Agent':'Mammoth/5.15.1 CFNetwork/975.0.3 Darwin/18.2.0'})
        weather_info = {}
        xml_blob_weather = ET.fromstring(weather_txt.text)
        weather_info['ReportText'] = xml_blob_weather.find(self.make_weather_xml_path('SnowReport', 'ReportText')).text
        weather_info['Snowfall24Hour'] = xml_blob_weather.find(self.make_weather_xml_path('SnowReport', 'Snowfall24Hour')).text
        weather_info['Snowfall48Hour'] = xml_blob_weather.find(self.make_weather_xml_path('SnowReport', 'Snowfall48Hour')).text
        weather_info['Snowfall72Hour'] = xml_blob_weather.find(self.make_weather_xml_path('SnowReport', 'Snowfall72Hour')).text
        weather_info['WindDescription'] = xml_blob_weather.find(self.make_weather_xml_path('Conditions', 'WindDescription')).text
        weather_info['TempuratureF'] = xml_blob_weather.find(self.make_weather_xml_path('Conditions', 'TempuratureF')).text
        weather_info['CurrentConditionName'] = xml_blob_weather.find(self.make_weather_xml_path('Conditions', 'CurrentConditionName')).text
        weather_info['Surface'] = xml_blob_weather.find(self.make_weather_xml_path('SnowReport', 'Surface')).text
        locations = xml_blob_weather.findall(self.make_weather_xml_path('SnowReport', 'Winds', 'Location'))
        weather_info['WindDetails'] = {}
        for location in locations:
            weather_info['WindDetails'][location.attrib['Name']] = location.attrib
        return(weather_info)

if __name__== "__main__":
    app = MammothMap()
    app.mainloop()
