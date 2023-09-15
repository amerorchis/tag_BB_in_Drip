import json
import requests
from BbApiConnector import BbApiConnector
import os
import tempfile
import concurrent.futures
from timeout_decorator import timeout, TimeoutError

try:
    from api.api_call import API_Search
except ModuleNotFoundError:
    from api_call import API_Search

def store_names(data):
    name_list = data['names'].split(', ')
    names_valid = list()

    # Sort out Jr. or IV or other non-name values that end up in the list.
    for i in name_list:
        i = i.strip()
        if i not in names_valid:
            if len(i) > 4:
                names_valid.append(i)
    
    email = data['email']
    batch = data['batch']
    # print(names_valid)
    return names_valid, email, batch

@timeout(8)
def blackbaud(names):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        bb_sec = os.environ['BB_CONFIG']
        bb_sec = json.loads(bb_sec)
        json.dump(bb_sec, tmp)
        tmp.close()
        api_conn = BbApiConnector(tmp.name)
        bb_session = api_conn.get_session()
        
        api = API_Search(names, bb_session)
        emails, errors = api.return_data()
        
    return emails, errors

if __name__ == "__main__":
    from test_names import names
    from datetime import datetime
    now = datetime.now()
    try:
        print(blackbaud(names))
        print(f'{datetime.now() - now} sec. for {len(names)} names')
    except TimeoutError:
        print(f'Timeout after {datetime.now() - now} sec.')

def generate_message(emails, errors, email, tagging_failed):
    recip = email[0].upper() + email[1:-12]
    no_tag = list()
    string = f'Hi {recip},\n\nThe following {len(emails) - len(no_tag)} people were tagged:\n'
    for i in range(len(emails)):
        if emails[i][0] not in tagging_failed:
            string += f'  •  {emails[i][1]}, {emails[i][0]}\n'
        else:
            no_tag.append(f'  •  {emails[i][1]}, {emails[i][0]}\n')
    cc = False
    
    if errors:
        string += '\nThe following people had either 0 or 2+ emails on record, so they could not be automatically tagged:\n'
        for i in errors:
            string += f'  •  {i}\n'
        cc = 'andrew@glacier.org'
    
    if no_tag:
        string += '\nThe following people had an email, but the Drip tagging step failed anyway:\n'
        for i in no_tag:
            string += i
        cc = 'andrew@glacier.org'

    return string, cc

def drip(emails):
    emails = [t[0] for t in emails]

    drip_token = os.environ['DRIP_TOKEN']
    account_ID = os.environ['DRIP_ACCOUNT']
    token = drip_token
    tagging_failed = list()

    authorization = f'Bearer {token}'
    headers = {"Authorization": authorization}
    url = f'https://api.getdrip.com/v2/{account_ID}/tags'

    def tag_email(email):
        payload= { 
            "tags": [{ 
                "email": email, 
                "tag": "Recent Gift" 
            }] 
        }
        data = json.dumps(payload)
        response = requests.post(url, headers=headers, data=data)
        success = 'successly tagged.' if response.status_code == 201 else 'tagging failed.'
        # print(f'{email} {success}')
        if success == 'tagging failed.':
            tagging_failed.append(email)
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(tag_email, email) for email in emails]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                pass
                # print(e)
    
    return tagging_failed
