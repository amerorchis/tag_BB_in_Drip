import json
from BbApiConnector import BbApiConnector
import os
import tempfile

try:
    from api.api_call import API_Search
except ModuleNotFoundError:
    from api_call import API_Search

def store_names(data):
    name_list = data['names']
    name_list = [i for i in name_list if len(i)>4]
    email = data['email']
    batch = data['batch']
    tag = data['tag']
    tag_state = data['tag_state']
    return name_list, email, batch, tag, tag_state

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
    print(blackbaud(names))
    print(f'{datetime.now() - now} sec. for {len(names)} names')

def generate_message(emails, errors, email, tagging_failed, tag, tag_state):
    req_type = 'tag' if tag_state else 'untag'
    recip = email[0].upper() + email[1:-12]
    no_tag = list()

    string = f'Hi {recip},\n\nThe following {len(emails) - len(errors)} people were {req_type}ged from \'{tag}\':\n'
    for i in range(len(emails)):
        if emails[i][0] not in tagging_failed:
            string += f'  •  {emails[i][1]}, {emails[i][0]}\n'
        else:
            no_tag.append(f'  •  {emails[i][1]}, {emails[i][0]}\n')
    cc = False
    
    if errors:
        string += f'\nThe following people had either 0 or 2+ emails on record, so they could not be automatically {req_type}ged:\n'
        for i in errors:
            string += f'  •  {i}\n'
        cc = 'andrew@glacier.org'
    
    if no_tag:
        string += f'\nThe following people had an email, but the Drip {req_type}ged step failed anyway:\n'
        for i in no_tag:
            string += i
        cc = 'andrew@glacier.org'

    return string, cc


