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

        if emails:
            tagging_failed = drip(emails, tag, tag_state)
        
        message, cc = generate_message(emails, errors, notification_email, tagging_failed, tag, tag_state)
        send_email(notification_email, cc, message, batch, tag_state)
        
        req_type = 'Tagging' if tag_state else 'Untagging'
        return jsonify(message=f"{req_type} Processed for {batch}. {len(emails)}/{len(names)} found. Confirmation sent to {notification_email}."), 200

    except Exception as e:
        message = e
        print(e)
        cc = 'andrew@glacier.org'
        notification_email = notification_email if notification_email else 'andrew@glacier.org'
        batch = batch if batch else ''
        send_email(notification_email, cc, message, batch)
        return jsonify(message=f"The server failed. A notification with logs was sent to you and Andrew."), 500
