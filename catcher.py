#-*- coding: utf-8 -*-
import getpass
import re
try: import readline
except: pass

from colorama import init as colorama_init
from colorama import Fore, Back, Style
from selenium import webdriver

from collections import namedtuple
from sys import stdout, stderr

URL_FACEBOOK = 'https://www.facebook.com/'
URL_FACEBOOK_USER = 'https://m.facebook.com/{0}'
RE_UID = re.compile('"([0-9]+)(?:\-[0-9]+)"')
STRUCT_USER = namedtuple('User', ['uid', 'name', 'image', 'url'])

driver = None

# get html source code from driver
def _get_source():
    source = ''
    if driver is not None:
        source = driver.page_source

    return source

# get single user data
def _get_user(uid):
    pass

# connect to facebook
def connect():
    result = False
    try:
        driver.get(URL_FACEBOOK)
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
def login(user, password):
    result = False

    # fill the inputbox
    user_field = driver.find_element_by_id('email')
    user_field.send_keys(user)
    pass_field = driver.find_element_by_id('pass')
    pass_field.send_keys(password)

    # submit
    form = driver.find_element_by_id('login_form')
    form.submit()

    if 'login.php' in driver.current_url:
        result = False
    else:
        result = True

    return result

# Fetch all user list from InitialChatFriendsList
def fetch_list():
    source = _get_source()
    if 'InitialChatFriendsList' not in source:
        raise TypeError
    
    pos = source.find('InitialChatFriendsList')
    block = source[pos:]
    pos = block.find('26]')  # Ends with "]}.26],"
    block = block[:pos]

    results = RE_UID.findall(block)
    users = []


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
    print >> stdout, Fore.YELLOW + 'Trying to sign in on Facebook..' + \
            Fore.RESET
    result = login(user, password)
    if result is False:
        print >> stderr, Fore.RED + 'Failed to sign in to Facebook' + \
                Fore.RESET
        exit(1)
    print >> stdout, Fore.GREEN + 'Logged in on Facebook' + Fore.RESET
    
    print >> stdout, Fore.CYAN + 'Getting list from Facebook' + Fore.RESET
    try:
        users = fetch_list()
    except TypeError:
        print >> stderr, Fore.RED + 'Failed to fetch page source' + Fore.RESET
        exit(1)
    

if __name__ == '__main__':
    main()

