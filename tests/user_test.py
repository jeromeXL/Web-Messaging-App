import pytest
from src.auth import auth_register_v1
from src.user import *
from src.error import *
from src.other import clear_v1
import requests
import json
from src import config
from src.config import url


@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def new_user_1():
    response = requests.post (config.url+ 'auth/register/v2', json={"email" : "a@a.com", "password": "aaaaaaaa", "name_first" : "a", "name_last": "a"})
    register = response.json()
    return register


#tests for user/profile/setname/v1

#test successful name change

""""""
def test_user_profile_setname(clear, new_user_1):  #change to blackbox
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1['token'], "name_first" : "frank", "name_last" : "sun"})
    assert response.status_code == 200


#tests when the first name is < 1 character

def test_user_profile_setname_first_empty(clear, new_user_1):
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1["token"], "name_first" : "", "name_last" : "Sun"})
    assert response.status_code == 400


#tests when the last name is < 1 character

def test_user_profile_setname_last_empty(clear, new_user_1):
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1['token'], "name_first" : "Frank", "name_last": ""})
    assert response.status_code == 400

    

#test when the first name given is > 50 characters

def test_user_profile_setname_long_first(clear, new_user_1):
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1['token'], "name_first" : "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "name_last" : "tree"})
    assert response.status_code == 400





#test when the last name given is >50 characters

def test_user_profile_setname_long_last(clear, new_user_1):
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1['token'], "name_first" : "frank", "name_last" : "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz" })
    assert response.status_code == 400
   
#invalid token


def test_user_profile_setname_invalid_token(clear, new_user_1):
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    response = requests.put (config.url + 'user/profile/setname/v1', json={"token" : new_user_1['token'], "name_first" : "frank", "name_last" : "sun"})
    assert response.status_code == 403

   


#tests for user_profile_setemail_v1

#test for successful email change


def test_user_setemail_success(clear, new_user_1):    #change to blackbox
    response = requests.put (config.url + 'user/profile/setemail/v1', json={"token" : new_user_1['token'], "email" : "frank@gmail.com"})
    assert response.status_code == 200

    

#test for invalid email():

def test_user_setemail_invalid(clear, new_user_1):
    response = requests.put (config.url + 'user/profile/setemail/v1', json={"token" : new_user_1['token'], "email" : "franksungmail.com"})
    assert response.status_code == 400

  

#test for duplicate email():

def test_user_setemail_duplicate(clear, new_user_1):    
    requests.post (config.url+ 'auth/register/v2', json={"email" : "darsh@gmail.com", "password": "aaaadada", "name_first" : "darsh", "name_last": "adalja"})
    response = requests.put (config.url + 'user/profile/setemail/v1', json = {"token" : new_user_1['token'], "email" : "darsh@gmail.com" })
    assert response.status_code == 400
   
   

# test for invalid token

def test_user_setemail_invalid_token(clear, new_user_1):
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    response = requests.put (config.url + 'user/profile/setemail/v1', json={"token" : new_user_1['token'], "email" : "frank@gmail.com"})
    assert response.status_code == 403



   

''' 
Test cases for user.py which contains functions user_profile_setname, user_profile_setemail, user_profile_sethandle
'''

import pytest
from src.auth import auth_register_v1
from src.user import *
from src.error import *
from src.other import clear_v1
import requests
import json
from src import config


''' Fixture that clears data_store and registers a valid user '''

@pytest.fixture
def clear_and_register1():
    requests.delete(config.url + 'clear/v1')
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register1 = response.json()
    return register1

''' Tests for user_profile_sethandle '''

''' Tests that a user is able to change their sethandle successfully when it is valid '''
def test_valid_sethandle(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": register2['token'], "handle_str": "bananas"})
    assert response2.status_code == 200
    response3 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": clear_and_register1['token'], "handle_str": "bananas"})
    assert response3.status_code == 400

''' Tests that an error is raised when the token is invalid '''
def test_sethandle_token_invalid(clear_and_register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response1 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": clear_and_register1['token'], "handle_str": "bananas"})
    assert response1.status_code == 403

''' Tests that an error is raised when the handle length is not between 3 and 50 characters '''
def test_handle_length_incorrect(clear_and_register1):
    response1 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": clear_and_register1['token'], "handle_str": "ab"})
    response2 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": clear_and_register1['token'], "handle_str": "abcdefghijklmnopqrstuvwxyz"})
    assert response1.status_code == 400
    assert response2.status_code == 400

''' Tests that an error is raised when the handle is not alphanumeric '''
def test_handle_not_alphanumeric(clear_and_register1):
    response1 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": clear_and_register1['token'], "handle_str": "H@l!0,%N"})
    assert response1.status_code == 400

''' Tests that an error is raised when the handle is taken by another user '''
def test_handle_used(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.put(config.url + 'user/profile/sethandle/v1', json={"token": register2['token'], "handle_str": "jameshunt"})
    assert response2.status_code == 400
    
'''Test user/all/v1, should return the user registered'''
def test_user_all_working(clear_and_register1):
    response2 = requests.get(config.url + "/users/all/v1", params={'token': clear_and_register1['token']})
    response_data = response2.json()
    assert response2.status_code == 200
    assert response_data['users'][0]['u_id'] == clear_and_register1['auth_user_id']
    
''' Tests that an error is raised when the token is invalid '''
def test_user_all_token_invalid(clear_and_register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response1 = requests.get(config.url + 'users/all/v1', params={"token": clear_and_register1['token']})
    assert response1.status_code == 403


''' User_profile tests'''
''' Test user proile of another user can be viewed'''
def test_user_profile_valid(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.get(config.url + 'user/profile/v1', params={"token": register2['token'], "u_id": clear_and_register1['auth_user_id']})
    assert response2.status_code == 200
    assert response2.json() == { 'user': 
    {
        'email': 'validemail@gmail.com',
        'handle_str': 'jameshunt',
        'name_last': 'Hunt',
        'name_first': 'James',
        'u_id': 1,
        'profile_img_url': f"{url}static/default.jpg"
    }
    }

''' Test user proile of yourself can be viewed'''
def test_user_profile_valid_self_profile(clear_and_register1):
    response2 = requests.get(config.url + 'user/profile/v1', params={"token": clear_and_register1['token'], "u_id": clear_and_register1['auth_user_id']})
    assert response2.status_code == 200
    print(response2.json())
    assert response2.json() == { 'user' : 
    {
        'email': 'validemail@gmail.com',
        'handle_str': 'jameshunt',
        'name_last': 'Hunt',
        'name_first': 'James',
        'u_id': 1,
        'profile_img_url': f"{url}static/default.jpg"
    }
    }

'''Test input error if u_id does not exist'''
def test_user_profile_input_error(clear_and_register1):
    response2 = requests.get(config.url + 'user/profile/v1', params={"token": clear_and_register1['token'], "u_id": clear_and_register1['auth_user_id'] + 3})
    assert response2.status_code == 400

''' Tests that an error is raised when the token is invalid '''
def test_profile_token_invalid(clear_and_register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response1 = requests.get(config.url + 'user/profile/v1', params={"token": clear_and_register1['token'], "u_id": clear_and_register1['auth_user_id']})
    assert response1.status_code == 403

''' User_profile_uploadphoto tests '''

''' Tests that an error is returned when an invalid token is given '''
def test_uploadphoto_invalid_token(clear_and_register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 200, 'y_end': 200 })
    assert response1.status_code == 403

''' Tests that an error is returned when an error occurs when attempting to retrieve the image '''
def test_uploadphoto_image_error(clear_and_register1):
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'hello', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 200, 'y_end': 200 })
    assert response1.status_code == 400

''' Tests that an error is returned when any of the dimensions for cropping giving are not in the dimensions of the image '''
def test_uploadphoto_dimensions_invalid(clear_and_register1):
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 2000, 'y_end': 2000 })
    assert response1.status_code == 400

''' Tests that an error is returned when the end dimensions are less than the start dimensions '''
def test_uploadphoto_end_less_than_start(clear_and_register1):
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': 50, 'y_start': 50, 'x_end': 10, 'y_end': 10 })
    assert response1.status_code == 400

''' Tests that an error is raised when negative dimensions are given '''
def test_uploadphoto_negative_dimensions(clear_and_register1):
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': -500, 'y_start': -500, 'x_end': -100, 'y_end': -100 })
    assert response1.status_code == 400

''' Tests that an error is returned when the image provided is not a jpg '''
def test_uploadphoto_not_jpg(clear_and_register1):
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://pngimg.com/uploads/potato/potato_PNG98084.png', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 200, 'y_end': 200 })
    assert response1.status_code == 400

''' Tests there are no errors when valid inputs are given '''
def test_uploadphoto_valid(clear_and_register1):
    requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    response1 = requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": clear_and_register1['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 200, 'y_end': 200 })
    assert response1.status_code == 200