import requests
import csv

PIPEDRIVE_API_BASE_URL = "https://hiredly.pipedrive.com/api/"


## Search for organization ##
def search_org(company_name: str, param: dict) -> str:
    search_params = param
    search_params["term"] = company_name
    search_params["fields"] = "name"

    search_response = requests.get(PIPEDRIVE_API_BASE_URL + "v1/organizations/search",
                                   params=search_params, verify=False)
    return str(search_response.json()['data']['items'][0]['item']['id'])


## Get organization details and last activity id ##
def get_org_last_activity_id(organization_id: str) -> str:
    param = {"api_token": API_TOKEN}
    org_detail_response = requests.get(
        PIPEDRIVE_API_BASE_URL + "v1/organizations/" + organization_id, params=param, verify=False)
    last_activity_id = org_detail_response.json()['data']['last_activity_id']
    return str(last_activity_id)


## Get person_id of primary participant of an activity ##
def get_primary_participant_id(activity_id: str) -> str:
    param = {"api_token": API_TOKEN}
    activity_response = requests.get(PIPEDRIVE_API_BASE_URL +
                                     "v1/activities/" + activity_id, params=param, verify=False)
    activity_participants = activity_response.json()['data']['participants']
    primary_participant_id = next(filter(
        lambda participant: participant['primary_flag'] is True, activity_participants))['person_id']
    return str(primary_participant_id)


## Get person object ##
def get_person(person_id: str):
    param = {"api_token": API_TOKEN}
    person = requests.get(PIPEDRIVE_API_BASE_URL +
                          "v1/persons/" + person_id, params=param, verify=False)
    return person.json()['data']

## Get name and primary email of person ##
def get_person_details(person_id: str):
    last_act_person = get_person(person_id)
    name = last_act_person['name']
    primary_email = last_act_person['primary_email']
    if primary_email.isspace():
        primary_email = next(filter(lambda email: email['primary'] is True, last_act_person['email']))['value']
    return {'name': name, 'email': primary_email}
    


##################################################################################################

if __name__ == "__main__":
    with open('credential.txt', 'r') as file:
        API_TOKEN = file.read().replace('\n', '')

    # with open('data/companylist.csv', newline='') as csvfile:
    #     companyreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    test_company_name = "Acer Sales & Services"

    # Search organization
    parameter = {"api_token": API_TOKEN}
    org_id = search_org(test_company_name, param=parameter)
    print(org_id)

    # Get organization details and last activity id
    last_activity_id = get_org_last_activity_id(org_id)
    print(last_activity_id)

    # Get activity
    last_act_primary_participant_id = get_primary_participant_id(
        last_activity_id)
    print(last_act_primary_participant_id)

    # Get person primary contact
    person_details = get_person_details(last_act_primary_participant_id)
    
    print("Company: " + test_company_name)
    print("Name: " + person_details['name'])
    print("Email: " + person_details['email'])
