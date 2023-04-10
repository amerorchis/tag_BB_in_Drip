from api.modules import *
from api.email_confirm import send_email

# main workflow
def main(data):
    names, notification_email, batch = store_names(data)
    emails, errors = blackbaud(names)
    message, cc = generate_message(names, emails, errors)
    
    drip(emails)
    send_email(notification_email, cc, message, batch)

    print(message)
    return(message)
