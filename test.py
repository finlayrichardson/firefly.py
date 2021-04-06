from driver import Firefly
from datetime import date

host = Firefly.get_host("ESMS")['url']
school = Firefly(host)

school.set_device_id("9ae53563-70e4-40c7-89e9-02dd75b560fa")
xml = open("auth.xml", "r").read()
school.complete_auth(xml)
print(school.verify_creds())
print(school.get_styles())
# print(school.graph_query(
#     f'mutation M{{result:tasks(ids:[92104],new_title:"Learn Exact Values",new_description:"Learn for radians and degrees",new_due:"2021-04-10")}}').text)
# print(school.graph_query(
#     f'mutation M{{result:tasks(ids:[39864],new_delete:true)}}').text)

# print(school.get_events(date.today(), date(2021, 12, 1)))