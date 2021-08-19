from driver import Firefly

host = Firefly.get_host("ESMS")['url']
school = Firefly(host)

print(school.set_device_id('3e1a14a7-5d55-47a4-bdff-90233e14ab37'))
print(school.get_auth_url())

xml = open("main.xml", "r").read()
school.complete_auth(xml)
# print(school.verify_creds())

# print(school.get_groups())


# 1. Run main.py
# 2. Copy first line (random code thing) into brackets after id on line 6 with quotes around it
# 3. Click on the link that was printed out
# 4. Login to firefly and copy the xml on that page into the file called auth.xml
# 5. Uncomment line 9-11 and run main.py again
# 6. If the program prints True, then it has worked
# 7. Uncomment line 13 and it will print your groups
# 8. Use https://jsonformatter.org/ to make it easier to read
