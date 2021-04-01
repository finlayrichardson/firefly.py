from driver import Firefly
from datetime import date

host = Firefly.get_host("ESMS")['url']
school = Firefly(host)

school.set_device_id("9ae53563-70e4-40c7-89e9-02dd75b560fa")
print(school.get_auth_url())
xml = open("auth.xml", "r").read()
school.complete_auth(xml)
print(school.get_events(date.today(), date(2021, 4, 23)))
