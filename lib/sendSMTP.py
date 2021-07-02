import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(SMTP_ADDR, SMTP_PW, subject_input, body_input, email_input):

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(SMTP_ADDR, SMTP_PW)

    # For each contact, send the email:
    for email in email_input:

        msg = MIMEMultipart()       # create a message

        # setup the parameters of the message
        msg['From'] = SMTP_ADDR
        msg['To'] = email
        msg['Subject'] = subject_input

        # add in the message body
        msg.attach(MIMEText(body_input, 'plain'))

        # send the message via the server set up earlier.
        s.sendmail(SMTP_ADDR, email, msg.as_string())
        del msg

    # Terminate the SMTP session and close the connection
    s.quit()

if __name__ == '__main__':
    send_email()
