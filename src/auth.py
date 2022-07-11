from src.data_store import data_store
from src.error import *
from src.config import url

import re
import hashlib
import jwt
import urllib.request
import sys
from random import getrandbits
from flask_mail import Message

SECRET = 'SEAMS'
SESSION_TRACKER = 0

'''
Provides the user_id for a user that has already been registered

Arguments:
    email (string)       - email that the account was registered with
    password (string)    - password that matches for the registered account, must be longer than 6 characters

Exceptions:
    InputError  - Occurs when email doesn't match a registered user or password is incorrect

Return Value:
    Returns auth_user_id and token on valid inputs
'''

def auth_login_v1(email, password):
    
    store = data_store.get()

    #Assuming email not found
    email_found = False
    #Checking for email in data_store and if password matches
    for user in store['users']:
        if user['email'] == email: 
            email_found = True
            if user['password'] == hashlib.sha256(password.encode()).hexdigest():
                session_id = generate_new_session()
                user['session_list'].append(session_id)
                user_id = user['u_id']
                token = jwt.encode({'auth_user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256') 
            else:
                raise InputError("Password is not correct")
    
    #Returning error if email not found
    if email_found == False:
        raise InputError("Email entered doesn't belong to a user")

    return {
        'token': token,
        'auth_user_id': user_id,
    }

'''
Registers a user and adds their information to data_store 

Arguments:
    email (string)       - email that the account is registered to and must match correct email format 
    password (string)    - password that must be longer than 6 characters
    name_first (string)  - first name of user that must be between 1 and 50 characters inclusive
    name_last (string)   - last name of user that must be between 1 and 50 characters inclusive

Exceptions:
    InputError  - Occurs when email doesn't match correct formation, email is already associated with a registered user, 
                    password is less than 6 characters or name_first or name_last are not between 1 and 50 characters inclusive

Return Value:
    Returns new auth_user_id and token on valid inputs
'''

def auth_register_v1(email, password, name_first, name_last):
    
    store = data_store.get()

    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    #Checking if inputs are of correct format
    if re.fullmatch(regex, email) == None:
        raise InputError("Invalid email")
    if len(password) < 6:
        raise InputError("Password not long enough")
    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError("First name incorrect length")
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError("First name incorrect length")

    #Checking if email is already assigned to a user
    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email already associated with a user")

    #Generating new user information 
    new_auth_id = len(store['users']) + 1
    if len(store['users']) == 0:
        permission_id = 1
    else:
        permission_id = 2 
    handle_str = generate_handle_str(name_first, name_last)
    handle_str = check_handle_str_exists(handle_str, store)
    password = hashlib.sha256(password.encode()).hexdigest()
    session_id = generate_new_session()
    token = jwt.encode({'auth_user_id': new_auth_id, 'session_id': session_id}, SECRET, algorithm='HS256')

    urllib.request.urlretrieve('http://i.kym-cdn.com/entries/icons/mobile/000/000/107/smily.jpg', "src/static/default.jpg")

    #Adding new user information to data store
    new_user = {'u_id': new_auth_id, 
                'email': email, 
                'name_first': name_first, 
                'name_last': name_last, 
                'handle_str': handle_str, 
                'password': password, 
                'permission_id': permission_id,
                'session_list': [session_id],
                'profile_img_url': f"{url}static/default.jpg" }
    store['users'].append(new_user)

    data_store.set(store)
    
    return {
        'token': token,
        'auth_user_id': new_auth_id,
    }

'''
Generates a new handle string for a user that is less than 20 characters by combining the first and last name

Arguments:
    name_first (string)  - first name of user that must be between 1 and 50 characters inclusive
    name_last (string)   - last name of user that must be between 1 and 50 characters inclusive

Return Value:
    Returns the new handle string
'''
def generate_handle_str(name_first, name_last):
    full_name = name_first + name_last
    lowercase_name = full_name.lower()
    handle_str = ''.join(character for character in lowercase_name if character.isalnum())
    if len(handle_str) > 20:
        handle_str = handle_str[0:20]
    return handle_str

'''
Checks if a user already has a given handle string and adds a number at the end accordingly

Arguments:
    handle_string (string)  - the basic handle string made by combining the first and last name
    store (dictionary)      - data store that contains all information stored related to seams 

Return Value:
    Returns new handle string which has a number appended if necessary 
'''
def check_handle_str_exists(handle_str, store):
    while any(user['handle_str'] == handle_str for user in store['users']):
        if handle_str[-1].isdigit() == False:
            handle_str = handle_str + '0'
        else:
            last_digit = int(handle_str[-1])
            new_last_digit = str(last_digit + 1)
            handle_str = handle_str[:-1] + new_last_digit 
    return handle_str

'''
Counts the total number of user sessions

Arguments:
    None 

Return Value:
    Returns the global variable SESSION TRACKER which is an integer and represents the total number of user sessions
'''
def generate_new_session():
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

'''
Invalidates a token to log out a user

Arguments:
    token (string)  - an authorisation hash that is valid if a user is logged in

Exceptions:
    AccessError     - Occurs when an invalid token is given (invalid user_id or user_session)

Return Value:
    Empty dictionary
'''
def auth_logout(token):
    
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']:
            session_id = decoded_token['session_id']
            user['session_list'].remove(session_id)
    
    return {}

'''
Decodes a given token and determines if it is valid

Arguments:
    store (dictionary)  - data store that contains all information stored related to seams 
    token (string)      - an authorisation hash that is valid if a user is logged in

Return Value:
    A dictionary containing:
        - Boolean true or false depending on whether the token is valid
        - auth_user_id of the user if found
        - session_id of the user if found
'''
def decode_token(store, token):
    
    active_user = jwt.decode(token, SECRET, algorithms=['HS256'])
    token_valid = False
    user_id = None
    session_id = None
    
    for user in store['users']:
        if user['u_id'] == active_user['auth_user_id'] and active_user['session_id'] in user['session_list']:
            token_valid = True
            user_id = user['u_id']
            session_id = active_user['session_id']
    
    return {'token_valid': token_valid,
            'u_id': user_id,
            'session_id': session_id}


'''
Given an email address, if the user is a registered user, sends them an email containing a specific secret code, that when entered in auth/passwordreset/reset, shows that the user trying to reset the password is the one who got sent this email. No error should be raised when passed an invalid email, as that would pose a security/privacy concern. When a user requests a password reset, they should be logged out of all current sessions.

Arguments:
    email (string)       - email that the account is registered to and must match correct email format 

Exceptions:
    N/A

Return Value:
    Returns email msg
'''

def auth_passwordreset_request_v1(email):

    store = data_store.get()

    for user in store['users']:
        if user['email'] == email:
            reset_code = getrandbits(32)
            msg = Message('UNSW Seams Password Reset', sender = 'GroupAnt1511@gmail.com', recipients = [f"{email}"])
            msg.body = f"Thank you for making a request to change your password. Enter the following code to reset your password: \n {reset_code}"
            for index, code in enumerate(store['reset_codes']):
                if user['email'] == code['email']:
                    store['reset_codes'].pop(index)
            store['reset_codes'].append({
                'email': user['email'],
                'reset_code': reset_code
            })
            return msg


'''

Given a reset code for a user, set that user's new password to the password provided. Once a reset code has been used, it is then invalidated.

Arguments:
    reset_code(int)             - a code unique to each attempt the user makes to reset password
    new_password                - password that must be longer than 6 characters

Exceptions:
    Input Error                 - If code is not valid
    Access Error                - If password is shorter than 6 characters

Return Value:
    Returns email msg
'''

def auth_password_reset_v1(reset_code, new_password):

    store = data_store.get()

    if len(new_password) < 6:
        raise AccessError("Password is too short")
    
    password = hashlib.sha256(new_password.encode()).hexdigest()

    for index, codes in enumerate(store['reset_codes']):
        if reset_code == codes['reset_code']:
            store['reset_codes'].pop(index)
            for user in store['users']:
                if user['email'] == codes['email']:
                    user['password'] = password
                    user['session_list'] = generate_new_session()
    
    raise InputError("Reset Code Not Valid")

