from api.modules import *
from api.email_confirm import send_email
from api.drip import drip
from flask import jsonify

# main workflow
def main(data):
    try:
        notification_email = ''
        batch = ''
        tagging_failed = []

        names, notification_email, batch, tag, tag_state = store_names(data)
        
        emails, errors = blackbaud(names)

        print("Errors: ", errors)

        if emails:
            tagging_failed = drip(emails, tag, tag_state)
            print("Failed: ", tagging_failed)
        

        if notification_email and 'test_only' not in tag:
            message, cc = generate_message(emails, errors, notification_email, tagging_failed, tag, tag_state)
            send_email(notification_email, cc, message, batch, tag_state)
        
        no_tag = errors + tagging_failed

        req_type = 'Tagging' if tag_state else 'Untagging'

        email_success = [i[1] for i in emails if i not in tagging_failed]
        email_fail = []

        for i in tagging_failed:
            emails = [i[0] for i in emails]
            if i in emails:
                index = emails.index(i)
                email_fail.append(emails[index][1])

        email_fail.extend([i for i in no_tag if len(i)>4])

        return jsonify(message=f"{req_type} Processed for {batch}. {len(emails)}/{len(names)} found.", outcome="Success!", success=email_success, fail=email_fail), 200

    except Exception as e:
        message = e
        print(e)
        cc = 'andrew@glacier.org'
        notification_email = notification_email if notification_email else 'andrew@glacier.org'
        batch = batch if batch else ''
        send_email(notification_email, cc, message, batch, tag_state)
        return jsonify(message=f"The server failed. A notification with logs was sent to you and Andrew.", outcome="Operation Failed"), 500
