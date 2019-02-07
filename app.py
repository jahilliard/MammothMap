import numpy as np
import time
import tkinter
import requests
import PIL.Image, PIL.ImageTk
import cv2
import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt
import datetime
import asyncio
import gzip
import shutil

class MammothMap(tkinter.Tk):
    curr_lift_state_hash = -1 
    curr_weather_state_hash = -1 
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
        self.run_update()

    async def log(self, log_type, data_type, data):
        today_date = dt.today()
        prefix = today_date.strftime('%y_%m') + "_" + log_type
        log_dir_name = 'log/' + prefix + "/"
        if not os.path.exists(log_dir_name):
            os.makedirs(log_dir_name)
        today_file_log_path = log_dir_name + today_date.strftime('%y_%m_%d') + "_" + log_type + "." + data_type 
        if not os.path.exists(today_file_log_path):
            yesterday_date = today_date - datetime.timedelta(days = 1)
            yester_prefix = yesterday_date.strftime('%y_%m') + "_" + log_type
            yester_log_dir_name = 'log/' + yester_prefix + "/"
            yester_file_log_path = yester_log_dir_name + yesterday_date.strftime('%y_%m_%d') + "_" + log_type + "." + data_type 
            if os.path.exists(yester_file_log_path):
                with open(yester_file_log_path, 'rb') as f_in:
                    with gzip.open(yester_file_log_path + '.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(yester_file_log_path)
        f=open(today_file_log_path, "a+")
        datetime_string = "<reqGetDateTime>" + today_date.strftime('%y-%m-%d-%H-%M') + "</reqGetDateTime>"
        f.write(data.replace('\n','') + datetime_string + '\n')
        f.close()

    def get_lift_information(self):
        curr_lift_state = []
        lift_status = requests.get('https://rp.trailtap.com/api/getMapDetails/mammoth?mapID=',
                headers = {'User-Agent':'Mammoth/5.15.1 CFNetwork/975.0.3 Darwin/18.2.0'})
        xml_blob = ET.fromstring(lift_status.text)
        current_hash = []
        for lift in xml_blob.iter('lift'):
            if lift.attrib['heading'] != 'Village Gondola':
                curr_lift = lift.attrib
                curr_lift['filename'] = self.lift_map[lift.attrib['heading']]
                curr_lift_state.append(curr_lift)
                current_hash.append(lift.attrib['heading'] + "=" + lift.attrib["status"])
        state_tuple = self.check_hash(":".join(sorted(current_hash)), self.curr_lift_state_hash)
        if state_tuple[0] == False:
            asyncio.run( self.log("lift_status", "xml", lift_status.text))
            self.curr_lift_state_hash = state_tuple[1]
        return(state_tuple[0], curr_lift_state)

    def check_hash(self, str_to_hash, compare_hash):
        current_hash = hash(str_to_hash)
        if current_hash == compare_hash: 
            return((True, -1))
        else:
            return((False, current_hash))

    def load_image(self, curr_lift_state):
        image = cv2.imread('mammothMountain.png')
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
    
    def run_update(self):
        print("checking Change")
        self.place_image()
        self.place_weather()
        self.after(2000, self.run_update)

    def place_image(self):
        curr_lift_state_tup = self.get_lift_information()
        if curr_lift_state_tup[0] == False:
            print("detected lift change")
            self.image = self.load_image(curr_lift_state_tup[1])
            self.photo = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.image))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            self.canvas.create_rectangle(1250, 700, 1750, 830, fill = "#ADD8E6")

    def place_weather(self):
        curr_weather_state_tup = self.get_weather_information()
        if curr_weather_state_tup[0] == False:
            print("detected weather change")
            weather = curr_weather_state_tup[1]
            self.canvas.create_text(1500, 720, text = '24 hour snow ' + weather['Snowfall24Hour'] + '\'')
            self.canvas.create_text(1500, 735, text = 'Tempurature is ' +weather['TempuratureF'])
            self.canvas.create_text(1500, 750, text = 'Current Conditions ' +weather['CurrentConditionName'])
            self.canvas.create_text(1500, 765, text = 'Current Surface ' +weather['Surface'])
            self.canvas.create_text(1500, 780, text = 'Current Summit Wind Speed ' +weather['WindDetails']['Summit']['Speed'])
            self.canvas.create_text(1500, 795, text = 'Current Summit Wind Direction ' +weather['WindDetails']['Summit']['Direction'])

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
        state_tuple = self.check_hash(weather_txt.text, self.curr_weather_state_hash)
        if state_tuple[0] == False:
            asyncio.run( self.log("weather", "xml", weather_txt.text))
            self.curr_weather_state_hash = state_tuple[1]
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
        return(state_tuple[0], weather_info)

if __name__== "__main__":
    app = MammothMap()
    app.mainloop()
