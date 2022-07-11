from src.data_store import data_store

from src.error import InputError
from src.error import AccessError
from src.auth import *
import urllib.request
import sys
from PIL import Image
import requests
import json
from src.config import url
import re


"""
USER PROFILE SETNAME:

Updates the authorised user's first and last name

Arguments: 
    token(string) - an authorisation hash that is valid if a user is logged in
    name_first(string) - the first name the user wants to change their current one to
    name_last(string) - the last name the user wants to change their current one to

Exceptions:
    InputError - length of name_first is not between 1 and 50 characters inclusive
    InputError - length of name_last is not between 1 and 50 characters inclusive
    AccessError - token is invalid
    
Return Value:
    {}
"""

def user_profile_setname_v1(token, name_first, name_last):
    
    store = data_store.get()

    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']:  
            if len(name_first) > 50 or len(name_first) < 1:
                raise InputError("length of name_first is not between 1 and 50 characters inclusive")  
            if len(name_last) > 50 or len(name_last) < 1:
                raise InputError("length of name_last is not between 1 and 50 characters inclusive")
            user['name_first'] = name_first
            user['name_last'] = name_last
            data_store.set(store)
            break
   
"""
USER PROFILE SETEMAIL:

Update the authorised user's email address

Arguments: 
    token(string) - an authorisation hash that is valid if a user is logged in  
    email - the email the user wants to change their current one to 

Exceptions:
    InputError - email entered is not a valid email
    InputError - email address is already being used by another user
    AccessError - invalid token

Return Value: 
    {}

"""

def user_profile_setemail_v1(token, email):
    
    store = data_store.get()
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    
    
    if re.fullmatch(regex, email) == None:
        raise InputError("email entered is not a valid email")
    

    for duplicate in store['users']:
        if duplicate['email'] == email:
            raise InputError("email address is already being used by another user")
  
    
    for user in store['users']:
        if user['u_id'] == decoded_token['u_id']:
            user['email'] = email
            data_store.set(store)
    



'''
Changes the handle string of a registered user given valid inputs

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    handle_string (string)  - the new handle string the user wants 

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    InputError  - Occurs when the provided handle string is not between 3 and 20 characters, 
                  not alphanumeric or used by another user

Return Value:
    Returns an empty dictionary
'''

def user_profile_sethandle(token, handle_str):
    
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Handle string length incorrect")
    elif handle_str.isalnum() == False:
        raise InputError("Handle string not alphanumeric")
    for user in store['users']:
        if handle_str == user['handle_str']:
            raise InputError("Handle string already used by another user")

    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            user['handle_str'] = handle_str
    
    data_store.set(store)

    return {}

'''
Returns profile details of the u_id given

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    u_id (int)              - user id of a given user

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    AccessError - Occurs if u_id is not valid

Return Value:
    Returns an empty dictionary
'''
def user_profile_v1(token, u_id):
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    all_users = store['users']
    user_found = False


    for user in all_users:
        if u_id == user['u_id']:
            user_found = True
            return { 'user' : 
            {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url']
            }
            }
    
    if user_found == False:
        raise InputError("U_id not valid")



"""
USERSALL

Returns a list of all users and their associated details. 

Arguments:
    token 
    ...

Exceptions:
    InputError  - NA
    AccessError - NA

Return Value:
    Returns users
"""


def users_all_v1(token):
    
    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    valid_users = []

    for user in store['users']:
        if user['email'] != '':
            user_info = {
                            'u_id': user['u_id'],
                            'email': user['email'],
                            'name_first': user['name_first'],
                            'name_last': user['name_last'],
                            'handle_str': user['handle_str'],
                            'profile_img_url': user['profile_img_url']
                        }
            valid_users.append(user_info)

    return {"users": valid_users}

"""
def user_profile_v1(token, u_id):
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    all_users = store['users']
    user_found = False


    for user in all_users:
        if u_id == user['u_id']:
            user_found = True
            return { 'user': 
            {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'nam_last': user['name_last'],
                'handle_string': user['handle_str']
            }
            }
    
    if user_found == False:
        raise AccessError("U_id not valid")

    """

'''
Uploads a photo for a user given a url and crops it according to the dimensions provided

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    img_url (string)        - the url of the image the user wants to upload
    x_start (int)           - x dimension for the start of the cropped image
    y_start (int)           - y dimension for the start of the cropped image
    x_end (int)             - x dimension for the end of the cropped image
    y_end (int)             - y dimension for the end of the cropped image

Exceptions:
    AccessError - Occurs when an invalid token is given 
    InputError  - Occurs when their is an issue retrieving the image using the url provided, 
                    any of the dimensions for cropping giving are not in the dimensions of the image,
                    the end dimensions are less than the start dimensions or the image provided is not a jpg

Return Value:
    Returns an empty dictionary
'''

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):

    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if x_end <= x_start or y_end <= y_start:
        raise InputError("End dimensions are less than or equal to start dimensions given")
    if x_start < 0 or y_start < 0:
        raise InputError("Cannot have negative dimensions")

    try:
        requests.get(img_url)
    except Exception as e: 
        raise InputError("Error occurred when attempting to retrieve image given") from e

    if img_url.endswith('.jpg') == False and img_url.endswith('.jpeg') == False:
        raise InputError("Image provided is not a jpg") 

    urllib.request.urlretrieve(img_url, f"src/static/user{decoded_token['u_id']}.jpg")

    imageObject = Image.open(f"src/static/user{decoded_token['u_id']}.jpg")
    width, height = imageObject.size
    if width < x_start or width < x_end or height < y_start or height < y_end:
        raise InputError("Dimensions provided are not within the dimensions of the image at the URL")

    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f"src/static/user{decoded_token['u_id']}.jpg")

    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            user['profile_img_url'] = f"{url}static/user{decoded_token['u_id']}.jpg"

    data_store.set(store)    

    return {}