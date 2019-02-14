import requests
import xml.etree.ElementTree as ET  

class Client(object):

    LIFTS_TO_SKIP = ['Village Gondola']

    def get_lift_status(self):
        curr_lift_state = []
        lift_status = requests.get('https://rp.trailtap.com/api/getMapDetails/mammoth?mapID=', 
                headers = {'User-Agent':'Mammoth/5.15.1 CFNetwork/975.0.3 Darwin/18.2.0'})
        xml_blob = ET.fromstring(lift_status.text)
        for lift in xml_blob.iter('lift'):
            if lift.attrib['heading'] in Client.LIFTS_TO_SKIP:
                continue
            curr_lift = lift.attrib
            curr_lift_state.append(curr_lift)
        curr_lift_state.sort(key=lambda x: x['myID'])
        return curr_lift_state
