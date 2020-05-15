########################################################
################### TRADING STRATEGY ###################
########################################################


### FUNCTIONS###

# def get_contacts(filename):
#     """Reads each line of contacts file,
#     and returns a tuple with the list of names and the list of email addresses"""
#     names = []
#     emails = []
#     with open(filename, mode='r', encoding='utf-8') as contacts_file:
#         for a_contact in contacts_file:
#             names.append(a_contact.split()[0])
#             emails.append(a_contact.split()[1])
#     return names, emails

# names, emails = get_contacts('mycontacts.txt')

### PACKAGES ###
from globalenv import *

### GLOBAL ENV ###
timezone = pytz.timezone("America/New_York")

smtp_server = "smtp.gmail.com"
sender_email = "tradingbot.guillem@gmail.com"
password = 'cekqer-2hyPsu-nerrev'
receiver_email = "gforto@gmail.com"


### FUNCTIONS ###
def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def substitute_in_msg(message_template, purchased, owned='/', sold='/', profitloss=0):
    now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    hour = str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
    day = str(now.day) + '/' + str(now.month) + '/' + str(now.year)
    message = message_template.substitute(  current_hour = hour,
                                            current_day = day,
                                            purchased_tickers = str(purchased),
                                            owned_tickers = str(owned),
                                            sold_tickers = str(sold),
                                            current_profitloss = str(profitloss))
    return(message)


def send_email(portfolio, profitloss_flt):
    # Set up the SMTP server
    context = ssl.create_default_context()
    s = smtplib.SMTP_SSL(smtp_server, port = 465, context=context)
    s.login(sender_email, password)

    # Message
    msg = MIMEMultipart()
        # body
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    portname = str(ny_now.year) + '-' + str(ny_now.month) + '-' + str(ny_now.day)
    msg_template = read_template('message.txt')
    purchased_dico = portfolio[portname]['bought']
    owned_dico = portfolio[portname]['owned']
    sold_dico = portfolio[portname]['sold']
    body = substitute_in_msg(   message_template = msg_template,
                                purchased = purchased_dico,
                                owned = owned_dico,
                                sold = sold_dico,
                                profitloss = profitloss_flt)
        # parameters
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Trading bot"
    msg.attach(MIMEText(body, 'plain'))
        # send the message via the server set up earlier.
    s.send_message(msg)
    del msg

    # Terminate the SMTP session and close the connection
    s.quit()
