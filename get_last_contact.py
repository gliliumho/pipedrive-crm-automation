import requests

with open('credential.txt', 'r') as file:
    API_TOKEN = file.read().replace('\n', '')

PIPEDRIVE_API_BASE_URL = "https://hiredly.pipedrive.com/api/"

params = {"api_token": API_TOKEN}

company_name = "Acer Sales & Services"

# Search organization
search_params = params
search_params["term"] = company_name
search_params["fields"] = "name"

search_response = requests.get(PIPEDRIVE_API_BASE_URL + "v1/organizations/search",
                               params=search_params, verify=False)
org_id = search_response.json()['data']['items'][0]['item']['id']
print(org_id)

# Get organization details and last activity id
#org_id = "6470"
params = {"api_token": API_TOKEN}
org_detail_response = requests.get(PIPEDRIVE_API_BASE_URL +
                                   "v1/organizations/" + str(org_id), params=params, verify=False)
last_activity_id = org_detail_response.json()['data']['last_activity_id']
print(last_activity_id)

# Get activity
last_activity_response = requests.get(PIPEDRIVE_API_BASE_URL +
                                      "v1/activities/" + str(last_activity_id), params=params, verify=False)
last_activity_participants = last_activity_response.json()[
    'data']['participants']
last_act_primary_participant_id = next(filter(
    lambda participant: participant['primary_flag'] is True, last_activity_participants))['person_id']
print(last_act_primary_participant_id)

# Get person primary contact
last_act_person = requests.get(PIPEDRIVE_API_BASE_URL +
                               "v1/persons/" + str(last_act_primary_participant_id), params=params, verify=False)
person_data = last_act_person.json()['data']
pname = person_data['name']
firstname = person_data['first_name']
lastname = person_data['last_name']
primary_email = next(filter(lambda email: email['primary'] is True, person_data['email']))['value']

print("Company: " + company_name)
print("Name: " + pname)
print("Email: " + primary_email)
