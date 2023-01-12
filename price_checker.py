import requests
from bs4 import BeautifulSoup as bsp
import configparser
import os
import time
import argparse
import re
import email
import smtplib


Email_Username = 'hordoandarius@gmail.com'
Email_Password = 'grsydslnkgfaszit'

cfg = configparser.ConfigParser()

parser = argparse.ArgumentParser()
parser.add_argument('-log', action='store_true', help='enable logging')
args = parser.parse_args()

logging = False

if args.log:
    logging = True

def execution_time(show_time):
    """"
        This function is a decorator and is used to see how long the request was made.
    """
    def timer(func):
        def time_counting(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            if show_time:
                print(f"The request was made in {end - start:.3f} seconds")
            return result
        return time_counting
    return timer

def configuration():
    """
        Configuration function is used to write default configuration in 'config.ini' file if the
        app is at the first running and the file doesn't exist, or to read configuration from 
        'config.ini' if already exist the file
    """
    if not os.path.exists('config.ini'):
        cfg.add_section('Request Options')
        cfg.set('Request Options', 'item', '')
        cfg.add_section('Price Checker')
        cfg.set('Price Checker', 'Under value', '400')
        cfg.set('Price Checker', 'Email receiver', 'random@example.com')
        with open('config.ini', 'w') as configfile:
            cfg.write(configfile)
            configfile.close()    
    else:
        cfg.read('config.ini')

def send_mail(fromMail, toMail, subject, content):
    """
        This function is used to send mails to a person using Email_Username and Email_Password defined at the begging of the script.
        Email_Username and Email_Password are the credentials for the sender mail.
    """
    msg = email.message.EmailMessage()
    msg['Subject'] = subject
    msg['From'] = fromMail
    msg['To'] = toMail
    msg.set_content(content)
    
    if fromMail.__contains__('yahoo'):
        domain_smtp = 'smtp.mail.yahoo.com'
    else:
        domain_smtp = f'smtp.{fromMail.split("@")[1]}'
        
    try:
        with smtplib.SMTP_SSL(domain_smtp, 465) as smtp:
        
            smtp.login(Email_Username, Email_Password)
            try:
                smtp.send_message(msg)
            except smtplib.SMTPServerDisconnected as e:
                print('Error: ', e)
    except smtplib.SMTPConnectError as e:
            print("The SMTP server couldn't be accessed: ", e)
    except smtplib.SMTPServerDisconnected as e:
        print('Error: ', e)
    
    
        
def get_input():
    """
        This function is used to get the input from the user. Firstly, function test if exist already in config.ini file an item. If doesn't exist,
        the user will have to enter data manually. If already exist an item in config.ini file, he will be prompt if want to insert new data or use 
        data from the config.ini file. 
    """
    option = '1'
    if cfg.get('Request Options', 'item') == '':
        option = '1'
    else:
        option = input('You want to use new data or load them from config.ini file?\n'+
                    '\tType 1 if you want to insert new data.\n'+
                    '\tType 2 if you want to use data from config.ini file.\n')
    if cfg.get('Request Options', 'item') == '' or option == '1':
        cfg.set('Request Options', 'item', input("Type what item you want to search: "))
        cfg.set('Price Checker', 'under value', input('Type under which value you want to receive an email about the item: '))
        while not cfg.get('Price Checker', 'under value').isdigit():
            cfg.set('Price Checker', 'under value', input('You entered a wrong value. Please enter a float number: '))
        cfg.set('Price Checker', 'Email receiver', input('Type on what mail you want to be noticed about items: '))
    return option


@execution_time(show_time = logging)
def make_request():
    """
        This function is used to make the request on olx.ro website. With this request we will get {ITEM} in order ascedant after the price.
        After that, the function will return the result as a beautiful soup object.
        If appear a connection error, the function will return -1.
    """
    url = f'https://www.olx.ro/d/oferte/q-{cfg.get("Request Options", "item").replace(" ", "-")}/?search[order]=filter_float_price:asc'
    try:
        response = requests.get(url)
    except requests.ConnectionError:
        print("The connection with the website couldn't be established. Try again.")
        return -1
    soup = bsp(response.text, 'html.parser')
    return soup
    
def analyze_request(soup):
    """
        This function will get the request response as BeautifulSoup object and search for each item's name and price. If the price is under
        'Under value' defined in config.ini file, it will use send_mail function to send an email on 'email receiver', defined also in config.ini file
        by the user.
    """
    for items in soup.find_all('div', {'data-cy': 'l-card'}):
        for item, price in zip(items.find_all('h6', {'class': 'css-ervak4-TextStyled er34gjf0'}), items.find_all('p', {'data-testid':'ad-price'})):
            if not price.text.lower().__contains__('schimb'):
                if int(re.sub(r'[a-zA-ZăâîșțĂÂÎȘȚ,. ]', '', price.text)) < int(cfg.get('Price Checker', 'Under value')):
                    print(item.text, price.text, ' is under value: ', cfg.get('Price Checker', 'Under value'))
                    send_mail(  Email_Username,
                                cfg.get('Price Checker', 'email receiver'),
                                f'{item.text} at {price.text}',
                                f'We found a {cfg.get("Request Options", "item")} under {cfg.get("Price Checker", "under value")}')


if __name__ == '__main__':
    configuration()
    option = get_input()
    response_soup = make_request()
    #If response_soup is -1 the request wasn't made succesfully.
    if response_soup == -1:
        exit()
    analyze_request(response_soup)
    #if option == 1 the user entered new data and the program will ask him if want to save the data in config file.
    if option == 1:
        update = input('Do you want to save the information in config.ini file? (y/n): ')
        if update == 'y':
            with open('config.ini', 'w') as configfile:
                cfg.write(configfile)
                configfile.close()
    