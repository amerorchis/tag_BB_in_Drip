import json
import requests
import os
import concurrent.futures

def drip(emails, tag, tag_status):
    emails = [t[0] for t in emails]

    drip_token = os.environ['DRIP_TOKEN']
    account_ID = os.environ['DRIP_ACCOUNT']
    token = drip_token
    tagging_failed = list()

    authorization = f'Bearer {token}'
    headers = {"Authorization": authorization}

    def tag_email(email):
        url = f'https://api.getdrip.com/v2/{account_ID}/tags'
        payload= { 
            "tags": [{ 
                "email": email, 
                "tag": tag
            }] 
        }
        data = json.dumps(payload)
        response = requests.post(url, headers=headers, data=data)
        success = 'successly tagged.' if response.status_code == 201 else 'tagging failed.'
        # print(f'{email} {success}')
        if success == 'tagging failed.':
            tagging_failed.append(email)
    
    def untag_email(email):
        url = f"https://api.getdrip.com/v2/{account_ID}/subscribers/{email}/tags/{tag}"
        
        response = requests.delete(url, headers=headers)
        success = 'successfully untagged.' if response.status_code == 204 else 'untagging failed.'
        if success == 'tagging failed.':
            tagging_failed.append(email)

    drip_function = tag_email if tag_status == True else untag_email

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(drip_function, email) for email in emails]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                pass
                # print(e)
    
    return tagging_failed
