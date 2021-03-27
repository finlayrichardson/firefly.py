import xml.etree.ElementTree as ET
import requests
from uuid import uuid4
from urllib.parse import quote

from requests.api import head


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
        if not hasattr(self, "deviceID"):
            self.set_device_id()
        redirect = quote(
            f"{self.host}/Login/api/gettoken?ffauth_device_id={self.deviceID}&ffauth_secret=&device_id={self.deviceID}&app_id={self.appID}")
        return f"{self.host}/login/login.aspx?prelogin={redirect}"

    def complete_auth(self, xml):
        token = ET.fromstring(xml)
        self.secret = token[0].text
        self.user = {'username': token[1].attrib['username'],
                     'fullname': token[1].attrib['fullname'],
                     'email': token[1].attrib['email'],
                     'role': token[1].attrib['role'],
                     'guid': token[1].attrib['guid']}
        self.classes = []
        for lesson in token[1][0]:
            self.classes.append({'guid': lesson.attrib['guid'],
                                 'name': lesson.attrib['name'],
                                 'subject': lesson.attrib['subject']})

    def graph_query(self, query):
        data = quote(query)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(f"{self.host}/_api/1.0/graphql?ffauth_device_id={self.deviceID}&ffauth_secret={self.secret}", data=data, headers=headers)

    def get_configuration(self):
        response = self.graph_query("""query Query {
				configuration {
					week_start_day, weekend_days, native_app_capabilities, notice_group_guid 
				}
			}""")  # Fix this
        print(response.text)


school = Firefly("https://esms.fireflycloud.net")

school.set_device_id()
print(school.get_auth_url())
input()
xml = open("auth.xml", "r").read()
school.complete_auth(xml)
school.get_configuration()
