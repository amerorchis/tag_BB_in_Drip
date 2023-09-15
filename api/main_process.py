from api.modules import *
from api.email_confirm import send_email
from api.chunk import chunk_names
from timeout_decorator import TimeoutError
from flask import jsonify

# main workflow
def main(data):
    try:
        notification_email = ''
        batch = ''
        
        names, notification_email, batch = store_names(data)

        if len(names)>25:
            return chunk_names(names, notification_email, batch)
        
        else:
            try:
                emails, errors = blackbaud(names)
            except TimeoutError:
                return jsonify(error="Timeout", message="The server could not complete the task within the specified time."), 504


            if emails:
                tagging_failed = drip(emails)
            
            message, cc = generate_message(emails, errors, notification_email, tagging_failed)
            send_email(notification_email, cc, message, batch)

    except Exception as e:
        message = e
        cc = 'andrew@glacier.org'
        notification_email = notification_email if notification_email else 'andrew@glacier.org'
        batch = batch if batch else ''
        send_email(notification_email, cc, message, batch)

    return jsonify(message=f"The server processed the request for batch {batch}. {len(emails)}/{len(names)} emails found. Confirmation of tagged emails sent to {notification_email}."), 200
