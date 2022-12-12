import webbrowser
import requests
from bs4 import BeautifulSoup as bsp
import configparser
import os

cfg = configparser.ConfigParser()

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
        
    return url, option

def make_request(url):
    """
        This function is used to make the request and return it as a beautifulsoup object.
    """
    response = requests.get(url)
    soup = bsp(response.text, 'html.parser')
    return soup

def analyze_request(soup):
    """
        This function will get the request response of the request as BeautifulSoup object and
        print the title and meta data for the page.
    """
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
        