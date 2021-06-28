import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = 'clnotifier1278@gmail.com'
PASSWORD = 'Ha$HloCk1278'

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = []
    emails = []
    with open(filename, mode='r') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the
    file specified by filename.
    """

    with open(filename, 'r') as template_file:    #encoding='utf-8'
        template_file_content = template_file.read()
    return Template(template_file_content)

def send_email(message_input, email_input):
    #names, emails = get_contacts('mycontacts.txt') # read contacts
    #message_template = read_template('messages.txt')

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for email in email_input:
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        #message = message_input.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        #print(message)

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']="This is TEST"

        # add in the message body
        msg.attach(MIMEText(message_input, 'plain'))

        # send the message via the server set up earlier.
        #s.send_message(msg)
        s.sendmail(MY_ADDRESS, email, msg.as_string())
        del msg

    # Terminate the SMTP session and close the connection
    s.quit()

if __name__ == '__main__':
    send_email()
