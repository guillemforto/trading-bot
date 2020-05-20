########################################################
####################### MAILING ########################
########################################################

### PACKAGES ###
import globalenv
from globalenv import *


### FUNCTIONS ###
def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def substitute_in_msg(message_template, purchased, profitloss, owned='/', sold='/'):
    now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
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
    s = smtplib.SMTP_SSL(globalenv.smtp_server, port = 465, context=context)
    s.login(globalenv.sender_email, globalenv.password)

    # Message
    msg = MIMEMultipart()
        # body
    msg_template = read_template('/Users/guillemforto/Desktop/trading-bot/message.txt') # message.txt
    purchased_dico = portfolio['bought']
    owned_dico = portfolio['owned']
    sold_dico = portfolio['sold']
    body = substitute_in_msg(   message_template = msg_template,
                                purchased = purchased_dico,
                                profitloss = profitloss_flt,
                                owned = owned_dico,
                                sold = sold_dico)
        # parameters
    msg['From'] = globalenv.sender_email
    msg['To'] = globalenv.receiver_email
    msg['Subject'] = "Trading bot"
    msg.attach(MIMEText(body, 'plain'))
        # send the message via the server set up earlier.
    s.send_message(msg)
    del msg

    # Terminate the SMTP session and close the connection
    s.quit()
