import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# make temp throwaway email account to send emails
MY_ADDRESS = 'clnotifier1278@gmail.com'
PASSWORD = ''


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


def send_email(subject_input, body_input, email_input):

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for email in email_input:

        msg = MIMEMultipart()       # create a message

        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']=subject_input

        # add in the message body
        msg.attach(MIMEText(body_input, 'plain'))

        # send the message via the server set up earlier.
        #s.send_message(msg)
        s.sendmail(MY_ADDRESS, email, msg.as_string())
        del msg

    # Terminate the SMTP session and close the connection
    s.quit()

if __name__ == '__main__':
    send_email()
