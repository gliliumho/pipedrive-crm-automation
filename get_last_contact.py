import requests
import csv
import configparser

# TODO: remove all verify=False for and re-enable warnings
import urllib3
urllib3.disable_warnings()

## Search for organization ##
def search_org(company_name: str, param: dict) -> dict:
    search_params = param
    search_params["term"] = company_name
    search_params["fields"] = "name"
    search_params["exact_match"] = True

    search_response = requests.get(PIPEDRIVE_API_BASE_URL + "v1/organizations/search",
                                   params=search_params, verify=False)
    top_result = search_response.json()['data']['items'][0]['item']

    return {'id': str(top_result['id']), 'name': top_result['name']}


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
    if not primary_email:
        primary_email = next(filter(
            lambda email: email['primary'] is True, last_act_person['email']))['value']
    return {'name': name, 'email': primary_email}


##################################################################################################
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_TOKEN = config['DEFAULT']['ApiToken']
    PIPEDRIVE_API_BASE_URL = config['DEFAULT']['PipeDriveUrl']

    company_detail_list = []
    with open('data/companylist.csv', newline='') as csvfile:
        companyreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in companyreader:
            search_company_name = row['name']
            print("Searching for company: " + search_company_name)

            # Search organization
            parameter = {"api_token": API_TOKEN}
            found_company = search_org(search_company_name, param=parameter)
            org_id = found_company['id']
            org_name = found_company['name']
            print("Found :" + org_name + " [" + org_id + "]")

            # Get organization details and last activity id
            last_activity_id = get_org_last_activity_id(org_id)

            # Get activity
            last_act_primary_participant_id = get_primary_participant_id(
                last_activity_id)

            # Get person primary contact
            person_details = get_person_details(
                last_act_primary_participant_id)

            company_detail_list.append(
                {'company_name': org_name, 'contact_name': person_details['name'], 'contact_email': person_details['email']})
            print("Name: " + person_details['name'])
            print("Email: " + person_details['email'])
            print("\n")

    print("Writing result to 'result.csv' file....")
    with open('result.csv', 'w', newline='') as csvfile:
        fieldnames = ["company_name", "contact_name", "contact_email"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in company_detail_list:
            writer.writerow(row)
