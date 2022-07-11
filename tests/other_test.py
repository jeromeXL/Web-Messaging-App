"""
tests for other

"""

import pytest
from src.other import *
from src.auth import *
from src.channels import *
from src.channel import *
from src.data_store import *
from src.error import *
from src.message import *
from src import config
import requests
import json

@pytest.fixture
def clear():
	""" Fixture that clears data_store before each test """
	requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register0():
	""" Fixture that registers a valid user0 """
	response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	register0 = response.json()
	return register0

@pytest.fixture
def channel0(register0):
	""" Fixture that creates a channel0 """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	channel0 = response.json()
	return channel0

'''
""" Test clear function """
def test_clear_function():
    """ clear """
    clear_v1()

""" Test raises error when cleared user """
def test_clear_user_error():
    """ clear with user_error """
    clear_v1()
    used_id = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1("validemail@gmail.com", "1234abcd") == used_id['auth_user_id']
    with pytest.raises(InputError):
        assert auth_login_v1("validemail@gmail.com", "1234abcd")

'''
""" Test raises error when cleared channel, user """   
'''    
def test_clear_channel_error():
    clear_v1()
    used_id = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
    temp_channel = channels_create_v1(used_id['auth_user_id'], "JeromeChiu", True)
    assert isinstance(temp_channel['channel_id'], int) == True
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1("validemail@gmail.com", "1234abcd") == used_id['auth_user_id']
    with pytest.raises(InputError):
        assert auth_login_v1("validemail@gmail.com", "1234abcd")
'''        
'''
"""      
def test_clear_messages():
    clear_v1()
    # create store
    initial_object = {
        'users': [],
        'channels_store': [
            {
                'name': 'channel A',
                'channel_id': 1001,
                'is_public': True,
                'owner_members': [2001, 2002],
                'all_members': [2001, 2002, 2003],
                'messages': [
                    {
                        'message_id': 1001,
                        'u_id': 2001,
                        'message': 'message 1',
                        'time_created': 1582426789,
                    }
                ]
            }
        ]
    }

    data_store.set(initial_object)

    #call clear
    clear_v1()

    result = channel_messages_v1(2001, 1001, 0)
   
    assert (0 == result['start'])
    assert (-1 == result['end'])
<<<<<<< HEAD

'''

""" clear """


def test_clear_function():
	""" test clear """
	response0 = requests.delete(config.url + 'clear/v1')
	assert response0.status_code == 200

def test_clear_user_error():
	""" Test raises error when cleared user """
	requests.delete(config.url + 'clear/v1')
	requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	requests.delete(config.url + 'clear/v1')
	response3 = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234abcd"})
	assert response3.status_code == 400

def test_clear_channel_error(register0):
	""" Test raises error when cleared channel, user """
	requests.delete(config.url + 'clear/v1')
	requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	requests.delete(config.url + 'clear/v1')
	response4 = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234abcd"})
	assert response4.status_code == 400

def test_clear_images(register0):
    """" Tests that no errors are raised when images are cleared """
    requests.post(config.url + 'user/profile/uploadphoto/v1', json={"token": register0['token'], 'img_url': 'http://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP.jpg', 
                                                                                'x_start': 0, 'y_start': 0, 'x_end': 200, 'y_end': 200 })
    response = requests.delete(config.url + 'clear/v1')
    assert response.status_code == 200