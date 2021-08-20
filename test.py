from driver import Firefly
from datetime import date

host = Firefly.get_host("ESMS")['url']
school = Firefly(host)

school.set_device_id("9ae53563-70e4-40c7-89e9-02dd75b560fa")
# print(school.get_auth_url())
xml = open("auth.xml", "r").read()
school.complete_auth(xml)
# print(school.verify_creds())
# print(school.get_styles())
# print(school.graph_query(
#     f'mutation M{{result:tasks(ids:[92104],new_title:"Learn Exact Values",new_description:"Learn for radians and degrees",new_due:"2021-04-10")}}').text)
# print(school.graph_query(
#     f'mutation M{{result:tasks(ids:[39864],new_delete:true)}}').text)
# print(school.get_groups())
print(school.get_events(date.today(), date(2021, 12, 1)))

# print(school.graph_query("""query Query {
#     users(guid: "DB:Cloud:DB:PASS:Stud:2662161") {
#         bookmarks {
#             simple_url, deletable, position, read, from {
#                 guid, name
#             }, type, title, is_form, form_answered, breadcrumb, guid, created
#         }, messages {
#             from {
#                 guid, name
#             }, sent, archived, id, single_to {
#                 guid, name
#             }, all_recipients, read, body
#         }, classes {
#             guid
#         }, children {
#             guid, name, sort_key
#         }, participating_in {
#             guid, sort_key, name, personal_colour
#         }, is_admin, sent_messages {
#             from {
#                 guid, name
#             }, sent, archived, id, all_recipients, read, body
#         }
#     }
# }""").text)
# print(school.get_tasks(2))
# print(school.get_task_ids())

# print(school.graph_query(
#     f'mutation M{{result:tasks(new:true,new_title:"hello tilly",new_description:"hi tilly how are you",new_set:"2021-08-20",new_due:"2021-12-10",new_setter:"{school.user["guid"]}",new_addressees:["{school.user["guid"]}"],new_task_type:"PersonalTask"){{id}}}}').text)

# print(school.set_personal_task("test", "this is a test", date(2021, 9, 10)))
