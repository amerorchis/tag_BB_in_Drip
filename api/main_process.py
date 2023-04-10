from api.modules import *
from api.email_confirm import send_email

# main workflow
def main(data):
    names, notification_email, batch = store_names(data)
    bb_data = blackbaud(names)
    emails = extract_emails(bb_data)
    message, cc = generate_message(names, emails)
    
    if not cc:
        drip(emails)
        pass
    
    send_email(notification_email, cc, message, batch)

    print(message)
    return(message)
