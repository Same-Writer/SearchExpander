import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(settings, subject_input, body_input, email_input):

    # set up the SMTP server
    s = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
    s.starttls()
    s.login(settings.smtp_addr, settings.smtp_pw)

    # For each contact, send the email:
    for email in email_input:

        msg = MIMEMultipart()       # create a message

        # setup the parameters of the message
        msg['From'] = settings.smtp_addr
        msg['To'] = email
        msg['Subject'] = subject_input

        # add in the message body
        msg.attach(MIMEText(body_input, 'plain'))

        # send the message via the server set up earlier.
        s.sendmail(settings.smtp_addr, email, msg.as_string())
        del msg

    # Terminate the SMTP session and close the connection
    s.quit()

if __name__ == '__main__':
    send_email()
