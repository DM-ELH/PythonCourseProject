import requests
from bs4 import BeautifulSoup as bsp
import configparser
import os
import time
import argparse

cfg = configparser.ConfigParser()

parser = argparse.ArgumentParser()
parser.add_argument('-log', action='store_true', help='enable logging')
args = parser.parse_args()

logging = False

if args.log:
    logging = True

def execution_time(show_time = logging):
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
        
        Default configuration:
            URL -> default is empty.
    """
    if not os.path.exists('config.ini'):
        cfg.add_section('Request Options')
        cfg.set('Request Options', 'URL', '')
        cfg.set('Request Options', 'item', '')
        with open('config.ini', 'w') as configfile:
            cfg.write(configfile)
            configfile.close()    
    else:
        cfg.read('config.ini')


def get_input():
    """
        This function is used to get the input the user. Firstly, user is asked if he want to use the URL from 
        the config file or want to enter the URL in terminal. If he choose the first options, the function will 
        return the URL from config file, otherwise, the user will be asked for the URL. The function return also
        the option that user chose because at the end of the program, the user will have the option to save the
        new URL (if he chose to enter the URL manually) in config file
    """
    
    if cfg.get('Request Options', 'URL') == '':
        option = '1'
    else:
        option = input("Type 1 to enter the URL from the command line\n"
                   + "Type 2 to use the URL from the config file\n")
    
    if option == '1':
        url = input("Enter the URL: ")
    elif option == '2':
        url = cfg.get('Request Options', 'URL')
    if url.__contains__('olx') and (option == '1' or cfg.get('Request Options', 'item') == ''):
        cfg.set('Request Options', 'item', input("Type what item you want to search: "))

    return url, option

@execution_time(show_time = logging)
def make_request(url):
    """
        This function is used to make the request and return it as a beautifulsoup object.
    """
    if not url.__contains__('https://wwww'):
        url = f'https://www.{url}'
    if not url.__contains__('olx') or cfg.get('Request Options', 'item') == '':
        response = requests.get(url)
    else:
        url = f'{url}/d/oferte/q-{cfg.get("Request Options", "item").replace(" ", "-")}/?search[order]=filter_float_price:asc'
        response = requests.get(url)
    soup = bsp(response.text, 'html.parser')
    return soup
    
def analyze_request(soup):
    """
        This function will get the request response of the request as BeautifulSoup object and
        print the title and meta data for the page.
    """
    if not soup.title.__contains__('OLX'):
        for items in soup.find_all('div', {'data-cy': 'l-card'}):
            for item, price in zip(items.find_all('h6', {'class': 'css-ervak4-TextStyled er34gjf0'}), items.find_all('p', {'data-testid':'ad-price'})):
                print(item.text, price.text, sep=" -> ")
    else:
        print(soup.title)
        for meta in soup.find_all('meta'):
            print(meta)
        
    

if __name__ == '__main__':
    configuration()
    URL, option = get_input()
    response_soup = make_request(URL)
    analyze_request(response_soup)
    if option == '1':
        update = input('Do you want to save the current URL in config file? (y/n): ')
        if update == 'y':
            cfg.set('Request Options', 'url', URL)
            with open('config.ini', 'w') as configfile:
                cfg.write(configfile)
                configfile.close()
    