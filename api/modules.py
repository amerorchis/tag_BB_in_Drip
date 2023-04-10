import json
import requests
from BbApiConnector import BbApiConnector
from api.drip import *
import os
import tempfile

def store_names(data):
    name_list = data['names'].split(', ')
    names_valid = list()

    # Sort out Jr. or IV or other non-name values that end up in the list.
    for i in name_list:
        i = i.strip()
        if len(i) > 4:
            names_valid.append(i)
    
    email = data['email']
    batch = data['batch']
    return names_valid, email, batch

def blackbaud(names):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        bb_sec = os.environ['BB_CONFIG']
        bb_sec = json.loads(bb_sec)
        json.dump(bb_sec, tmp)
        tmp.close()
        api_conn = BbApiConnector(tmp.name)
        bb_session = api_conn.get_session()
        
        emails = list()
        errors = list()
        for name in names:
            r = bb_session.get(f'https://api.sky.blackbaud.com/constituent/v1/constituents/search?search_text={name}&strict_search=True')
            
            count = r.json()['count']
            if count == 1:
                emails.append(r.json()['value'][0]['email'].strip())
            else:
                errors.append(name)

    # Export the data for use in future steps
    print(f'\n\n\nEmails:{emails}\n')
    return emails, errors

def generate_message(names, emails, errors, email):
    recip = email[0].upper() + email[1:-12]
    string = f'Hi {recip},\n\nThe following people were tagged:\n'
    for i in range(len(emails)):
        string += f'• {names[i]}, {emails[i]}\n'
    cc = False
    
    if errors:
        string += '\nThe following people had multiple emails on record, so they could not be automatically tagged:\n'
        for i in errors:
            string += f'• {i}\n'
        cc = 'andrew@glacier.org'

    return string, cc

def drip(emails):
    drip_token = os.environ['DRIP_TOKEN']
    account_ID = os.environ['DRIP_ACCOUNT']
    token = drip_token

    authorization = f'Bearer {token}'
    headers = {"Authorization": authorization}
    url = f'https://api.getdrip.com/v2/{account_ID}/tags'

    for email in emails:
        payload= { 
            "tags": [{ 
                "email": email, 
                "tag": "Recent Gift" 
            }] 
            }
        data = json.dumps(payload)
        response = requests.post(url, headers=headers, data=data)
        success = 'successly tagged.' if response.status_code == 201 else 'tagging failed.'
        print(f'{email} {success}')
    
    print()
