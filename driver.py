import xml.etree.ElementTree as ET
import requests
from uuid import uuid4
from urllib.parse import quote
from requests.models import Response
from datetime import date


class Firefly:
    def __init__(self, host: str, appID: str = "Firefly.py Driver"):
        if not host:
            raise Exception("Invalid host")
        self.host = host
        self.appID = appID

    @staticmethod
    def get_host(code: str, appId: str = 'Firefly.py Driver', deviceID: str = None) -> dict:
        """Gets information about the host from a code"""
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
                'deviceID': str(deviceID)}

    def get_api_version(self) -> dict:
        """Gets the version of the API"""
        response = requests.get(self.host + "/login/api/version")
        response = ET.fromstring(response.content)
        return {'major': int(response[0].text),
                'minor': int(response[1].text),
                'increment': int(response[2].text)}

    def set_device_id(self, id: str = None) -> str:
        """Sets the device ID to a specified string, or creates one if nothing is passed"""
        if not id:
            id = str(uuid4())
        self.deviceID = id
        return id

    def get_auth_url(self) -> str:
        """Gets an authorisation URL"""
        if not hasattr(self, "deviceID"):
            self.set_device_id()
        redirect = quote(
            f"{self.host}/Login/api/gettoken?ffauth_device_id={self.deviceID}&ffauth_secret=&device_id={self.deviceID}&app_id={self.appID}")
        return f"{self.host}/login/login.aspx?prelogin={redirect}"

    def complete_auth(self, xml: str):
        """Parses the information from the xml"""
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

    def verify_creds(self) -> bool:
        """Verifies whether the user is logged in correctly"""
        if not hasattr(self, "deviceID") or not hasattr(self, "secret"):
            return False
        response = requests.get(
            f"{self.host}/Login/api/verifytoken?ffauth_device_id={self.deviceID}&ffauth_secret={self.secret}")
        if response.json()['valid']:
            return True
        return False

    def graph_query(self, query: str) -> Response:
        """Sends a GraphQL query to the API endpoint"""
        data = {"data": query}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(f"{self.host}/_api/1.0/graphql?ffauth_device_id={self.deviceID}&ffauth_secret={self.secret}", data=data, headers=headers)

    def get_configuration(self) -> dict:
        """Gets the configuration of the school"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query("""query Query {
				configuration {
					week_start_day, weekend_days, native_app_capabilities, notice_group_guid 
				}
		    }""").json()

    def get_styles(self) -> dict:
        """Gets the styles"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query("""query Query {
				app_styles {
					value, name, type, file 
				}
			}""").json()

    def get_bookmarks(self) -> dict:
        """Gets the user's bookmarks"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query(f"""query Query {{
				users(guid: "{self.user['guid']}") {{
					bookmarks {{
						simple_url, deletable, position, read, from {{
							guid, name 
						}}, type, title, is_form, form_answered, breadcrumb, guid, created 
					}}
				}}
			}}""").json()

    def get_messages(self) -> dict:
        """Gets the user's messages"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query(f"""query Query {{
				users(guid: "{self.user['guid']}") {{
					messages {{
						from {{
							guid, name 
						}}, sent, archived, id, single_to {{
							guid, name 
						}}, all_recipients, read, body 
					}}
				}}
			}}""").json()

    def get_groups(self) -> dict:
        """Gets the groups that the user is part of"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query(f"""query Query {{
				users(guid: "{self.user['guid']}") {{
					participating_in {{
						guid, sort_key, name, personal_colour 
					}}
				}}
			}}""").json()

    def get_events(self, start: date, end: date) -> dict:
        """Gets all events within a specified time range, passed in as start and end"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query(f"""query Query {{
				events(start: "{start.strftime("%Y-%m-%dT%H:%M:%SZ")}", for_guid: "{self.user['guid']}", end: "{end.strftime("%Y-%m-%dT%H:%M:%SZ")}") {{
					end, location, start, subject, description, guild, attendees {{ role, principal {{ guid, name }}}}
				}}
			}}""").json()

    def get_tasks(self) -> dict:
        """Get the user's tasks"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = f"""{{
                    "archiveStatus": "All",
                    "completionStatus": "Todo",
                    "ownerType": "OnlySetters",
                    "page": 0,
                    "pageSize": 100,
                    "sortingCriteria": [
                        {{
                        "column": "DueDate",
                        "order": "Descending"
                        }}
                    ]
                    }}"""
        return requests.post(f"{self.host}/api/v2/taskListing/view/student/tasks/all/filterBy?ffauth_device_id={self.deviceID}&ffauth_secret={self.secret}", data=data, headers=headers).json()

    def set_personal_task(self, title: str, description: str, due_date: date) -> dict:
        """Set's a personal task"""
        if not hasattr(self, "user"):
            raise Exception("User not authenticated")
        return self.graph_query(f"""mutation M {{
                result:tasks(new:true,new_title:"{title}",new_description:"{description}",new_set:"{date.today().strftime("%Y-%m-%d")}",new_due:"{due_date.strftime("%Y-%m-%d")}",new_setter:"{self.user["guid"]}",new_addressees:["{self.user["guid"]}"],new_task_type:"PersonalTask")
                    {{
                        id
                    }}
                }}""").json()
