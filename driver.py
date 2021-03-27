import xml.etree.ElementTree as ET
import requests
from uuid import uuid4
from urllib.parse import quote


class Firefly:
    def __init__(self, host, appID="Firefly.py Driver"):
        if not host:
            raise Exception("Invalid host")
        self.host = host
        self.appID = appID

    @staticmethod
    def get_host(code, appId='Firefly.py Driver', deviceID=None):
        if not deviceID:
            deviceID = uuid4()
        response = requests.get(
            f"https://appgateway.fireflysolutions.co.uk/appgateway/school/{code}")
        response = ET.fromstring(response.content)
        if not eval(response.attrib['exists'].title()):
            raise Exception("Invalid response")

        host = response[1].text
        ssl = eval(response[1].attrib['ssl'].title())
        if ssl:
            url = "https://" + host
        else:
            url = "http://" + host
        tokenURL = quote(
            f"{url}/Login/api/gettoken?ffauth_device_id={deviceID}&ffauth_secret=&device_id={deviceID}&app_id={appId}")

        return {'enabled': eval(response.attrib['exists'].title()),
                'name': response[0].text,
                'id': response[2].text,
                'host': host,
                'ssl': ssl,
                'url': url,
                'tokenURL': tokenURL,
                'deviceID': deviceID}

    def get_api_version(self):
        response = requests.get(self.host + "/login/api/version")
        response = ET.fromstring(response.content)
        return {'major': int(response[0].text),
                'minor': int(response[1].text),
                'increment': int(response[2].text)}

    def set_device_id(self, id=None):
        if not id:
            id = uuid4()
        self.deviceID = id
        return id

    def get_auth_url(self):
        if not self.deviceID:
            self.set_device_id()
        redirect = quote(
            f"{self.host}/Login/api/gettoken?ffauth_device_id={self.deviceID}&ffauth_secret=&device_id={self.deviceID}&app_id={self.appID}")
        return f"{self.host}/login/login.aspx?prelogin={redirect}"


school = Firefly.get_host("ESMS")
print(school)
