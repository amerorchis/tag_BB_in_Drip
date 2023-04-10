from api.modules import *
from api.email_confirm import send_email

# main workflow
def main(data):
    try:
        notification_email = ''
        batch = ''
        names, notification_email, batch = store_names(data)
        emails, errors = blackbaud(names)
        message, cc = generate_message(names, emails, errors, notification_email)
    except Exception as e:
        message = e
        cc = 'andrew@glacier.org'
    
    notification_email = notification_email if notification_email else 'andrew@glacier.org'
    batch = batch if batch else ''

    if emails:
        drip(emails)
    
    send_email(notification_email, cc, message, batch)

    print(message)
    return(message)
