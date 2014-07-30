#-*- coding: utf-8 -*-
import getpass
import re
import requests
try: import readline
except: pass

from colorama import init as colorama_init
from colorama import Fore, Back, Style
from selenium import webdriver

from collections import namedtuple
from sys import argv, stdout, stderr
from tabulate import tabulate

URL_FACEBOOK = 'https://www.facebook.com/'
URL_FACEBOOK_USER = 'https://m.facebook.com/{0}'
RE_UID = re.compile('"([0-9]+)(?:\-[0-9]+)"')
RE_TITLE = re.compile('<title>(.+)</title>')
STRUCT_USER = namedtuple('User', ['uid', 'name', 'url'])

cookies = {}
session = requests.Session()
driver = None

# get html source code from driver
def _get_source():
    source = ''
    if driver is not None:
        source = driver.page_source

    return source

# using a session cookie from selenium in urllib/urllib2/requests
def _set_cookie():
    all_cookies = driver.get_cookies()
    for cookie in all_cookies:
        cookies[cookie['name']] = cookie['value']

# get single user data
def _get_user(uid):
    user = None
    url = URL_FACEBOOK_USER.format(uid)
    try:
        s = session.get(url, cookies=cookies)
        title = RE_TITLE.search(s.content).group(1)
        print s.url
        if '.' not in title:
            name = title.decode('utf-8')
            url = s.url.replace('m.facebook.com', 'fb.me').replace(
                    '?_rdr', '')
            user = STRUCT_USER(uid=uid, name=name, url=url)
    except Exception, e:
        pass
    
    return user

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

    _set_cookie()
    return result

# Fetch all user list from InitialChatFriendsList
def fetch_list(limit=50):
    source = _get_source()
    if 'InitialChatFriendsList' not in source:
        raise TypeError
    
    pos = source.find('InitialChatFriendsList')
    block = source[pos:]
    pos = block.find('26]')  # Ends with "]}.26],"
    block = block[:pos]

    results = RE_UID.findall(block)
    yield results
    
    results = results[:limit]
    users = []
    for uid in results:
        user = _get_user(uid)
        if user is not None:
            users.append(user)
    yield users

# Print as pretty table
def print_table(data):
    organized = []
    print tabulate(data)

def main(limit):
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
    generator = fetch_list(limit)
    try:
        users = generator.next() 
    except TypeError:
        print >> stderr, Fore.RED + 'Failed to fetch page source' + Fore.RESET
        exit(1)
    
    cnt = len(users)
    print >> stdout, Fore.BLUE + 'Loaded {0} users'.format(cnt) + Fore.RESET
    
    print >> stdout, Fore.CYAN + \
            'Getting top {0} users detailed data..'.format(limit) + \
            Fore.RESET
    final = generator.next()
    
    print_table(final)

if __name__ == '__main__':
    try:
        limit = int(argv[1])
    except:
        print >> stderr, 'Please input first argument as Integer ' + \
                '(Need for limit results)'
    else:
        main(limit=limit)

