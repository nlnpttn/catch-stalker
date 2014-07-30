#-*- coding: utf-8 -*-
import urls
import getpass
try: import readline
except: pass

from colorama import init as colorama_init
from colorama import Fore, Back, Style
from selenium import webdriver

from sys import stdout, stderr

driver = None

# connect to facebook
def connect():
    result = False
    try:
        driver.get(urls.Facebook.main)
        result = True
    except Exception, e:
        print e
        result = False

    return result

# read username, password from stdin
def prompt():
    username, password = '', ''
    while username == '':
        username = raw_input('Username: ')
    while password == '':
        password = getpass.getpass()
    
    return (username, password)

# sign in to facebook
def login():
    pass

def main():
    global driver

    colorama_init()
    print >> stdout, Fore.YELLOW + 'Initializing selenium..' + Fore.RESET
    try:
        driver = webdriver.PhantomJS()
        if driver is None:
            raise TypeError
    except:
        print >> stderr, Fore.RED + 'An error occurred while launching ' + \
                'selenium(PhantomJS).' + Fore.RESET
        exit(1)
    
    print >> stdout, Fore.YELLOW + 'Connecting to Facebook..' + Fore.RESET
    result = connect()
    if result is False:
        print >> stderr, Fore.RED + 'Failed to connect to Facebook' + \
                Fore.RESET
        exit(1)

    user, password = prompt()

if __name__ == '__main__':
    main()

