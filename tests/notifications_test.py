import pytest
from src.standup import *
from src.error import InputError, AccessError
from src.other import *
from src.channel import *
from src.notifications import *
import jwt
import time
from datetime import datetime 


from src.auth import *
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.channel import channel_join_v2
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src.data_store import data_store
from src.user import *

import requests
import json
from src import config


''' Fixture that clears data_store before each test '''
@pytest.fixture
def clear():
	requests.delete(config.url + 'clear/v1')

''' Fixture that registers a valid user '''
@pytest.fixture
def register1():
	response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	register1 = response.json()
	return register1

''' Fixture that registers a valid user '''
@pytest.fixture
def register2():
	response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail1@gmail.com", "password": "1234abcd", "name_first": "Ashna", "name_last": "Desai"})
	register2 = response.json()
	return register2
''' Fixture that registers a valid user '''
@pytest.fixture
def register3():
	response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "John", "name_last": "Doe"})
	register3 = response.json()
	return register3

''' Tests for notifications'''

''' tests for valid output when user is added to a channel'''
def test_notifications_addedchannels(clear, register1, register2):
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register1['token'], "name": "test", "is_public": True})
    channel = response1.json()
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : register1['token'], "channel_id" : channel['channel_id'], "u_id" : register2['auth_user_id']})
    assert response.status_code == 200
    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register2['token']})
    assert notifications.status_code == 200
    notification = notifications.json()
    assert notification == { 'notifications':
    [
    {
        'channel_id': channel['channel_id'],
        'dm_id': -1,
        'notification_message': "jameshunt added you to test"
    }
    ]
    }

''' tests for valid output when user is added to a dm'''
def test_notifications_addeddms(clear, register1, register2, register3):
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": register1['token'], "u_ids": [register2['auth_user_id'], register3['auth_user_id']]})
    dm_created1 = response3.json()
    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register2['token']})
    assert notifications.status_code == 200
    notification = notifications.json()
    assert notification == { 'notifications': 
    [
    {
        'channel_id': -1,
        'dm_id': dm_created1['dm_id'],
        'notification_message': "jameshunt added you to ashnadesai, jameshunt, johndoe"
    }
    ]
    }


''' tests for valid output when user's messages are reacted to in a channel'''
def test_notifications_reactchannels(clear, register1, register2, register3):

    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register1['token'], "name": "test", "is_public": True})
    channel = response1.json()

    #make users join channels
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : register3['token'], "channel_id" : channel['channel_id']})
    

    #send messages in channel1
    a = requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel["channel_id"], "message": "Hiiiiiii"})
    message = a.json()
    requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel["channel_id"], "message": "Hello"})
    c = requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel["channel_id"], "message": "bonjour"})
    message2 = c.json()
    

    #react to messages
    requests.post(config.url + 'message/react/v1', json={"token" : register3['token'], "message_id" : message["message_id"], "react_id" : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], "message_id" : message["message_id"], "react_id" : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], 'message_id' : message2['message_id'], 'react_id' : 1 })
    requests.post(config.url + 'message/react/v1', json={"token" : register3['token'], 'message_id' : message2['message_id'], 'react_id' : 1})


    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register1['token']})
    assert notifications.status_code == 200

    notification = notifications.json()
    assert notification == { 'notifications':
        [
        {
            'channel_id': channel['channel_id'],
            'dm_id': -1,
            'notification_message': 'johndoe reacted to your message in test'},
        {
            'channel_id': 1,
            'dm_id': -1,
            'notification_message': 'ashnadesai reacted to your message in test'
        },
        {
            'channel_id': 1,
            'dm_id': -1,
            'notification_message': 'ashnadesai reacted to your message in test'
        },
        {
            'channel_id': 1,
            'dm_id': -1,
            'notification_message': 'johndoe reacted to your message in test'
        },
        ]
    }


''' tests for valid output when user's messages are reacted to in a dm'''
def test_notifications_reactdms(clear, register1, register2, register3):

    response3 = requests.post(config.url + 'dm/create/v1', json={"token": register1['token'], "u_ids": [register2['auth_user_id'], register3['auth_user_id']]})
    dm_created1 = response3.json()
    

    #send messages in dm_created1
    response1 = requests.post(config.url + 'message/senddm/v1', json={"token": register1["token"], "dm_id": dm_created1['dm_id'], "message": "H"})
    message1 = response1.json()
    response2 = requests.post(config.url + 'message/senddm/v1', json={"token": register1["token"], "dm_id": dm_created1['dm_id'], "message": "Hiii"})
    message2 = response2.json()
    response3 = requests.post(config.url + 'message/senddm/v1', json={"token": register1["token"], "dm_id": dm_created1['dm_id'], "message": "Hello"})
    message3 = response3.json()
    

    #react to messages
    requests.post(config.url + 'message/react/v1', json={"token" : register3['token'], "message_id" : message1["message_id"], "react_id" : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], "message_id" : message1["message_id"], "react_id" : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register3['token'], 'message_id' : message2['message_id'], 'react_id' : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], 'message_id' : message2['message_id'], 'react_id' : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], 'message_id' : message3['message_id'], 'react_id' : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register3['token'], 'message_id' : message3['message_id'], 'react_id' : 1})


    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register1['token']})
    assert notifications.status_code == 200

    notification = notifications.json()
    assert notification == { 'notifications': 
        [
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'johndoe reacted to your message in ashnadesai, jameshunt, johndoe'},
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'ashnadesai reacted to your message in ashnadesai, jameshunt, johndoe'
        },
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'ashnadesai reacted to your message in ashnadesai, jameshunt, johndoe'
        },
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'johndoe reacted to your message in ashnadesai, jameshunt, johndoe'
        },
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'ashnadesai reacted to your message in ashnadesai, jameshunt, johndoe'
        },
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'johndoe reacted to your message in ashnadesai, jameshunt, johndoe'
        },
        ]
    }

''' Tests for valid output when user is tagged in a channel message'''
def test_notifications_tagging_send(clear, register1, register2, register3):

    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register1['token'], "name": "test", "is_public": True})
    channel = response1.json()

    #make users join channels
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : register3['token'], "channel_id" : channel['channel_id']})

    #send messages in channel1
    requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel["channel_id"], "message": "Hiiiiiii Ashna How are you today? @ashnadesai"})
    
    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register2['token']})
    assert notifications.status_code == 200

    notification = notifications.json()
    assert notification == {'notifications':
    [
        {
            'channel_id': 1,
            'dm_id': -1,
            'notification_message': 'jameshunt tagged you in test: Hiiiiiii Ashna How a'},
    ]
    }

''' Tests for valid output when user is tagged in a channel message and handle_str is tagged incorrectly'''
def test_notifications_tagging_send2(clear, register1, register2, register3):

    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register1['token'], "name": "test", "is_public": True})
    channel = response1.json()

    #make users join channels
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : register3['token'], "channel_id" : channel['channel_id']})

    #send messages in channel1
    requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel["channel_id"], "message": "Hiiiiiii Ashna H@ashnaow are you today? @ashnadesai"})
    
    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register2['token']})
    assert notifications.status_code == 200

    notification = notifications.json()
    assert notification == { 'notifications':
    [
        {
            'channel_id': 1,
            'dm_id': -1,
            'notification_message': 'jameshunt tagged you in test: Hiiiiiii Ashna H@ash'},
    ]
    }

''' Tests for valid output when user is tagged in a dm message'''
def test_notifications_tagging_send_dm(clear, register1, register2, register3):

    response3 = requests.post(config.url + 'dm/create/v1', json={"token": register1['token'], "u_ids": [register2['auth_user_id'], register3['auth_user_id']]})
    dm_created1 = response3.json()
    

    #send messages in dm_created1
    requests.post(config.url + 'message/senddm/v1', json={"token": register1["token"], "dm_id": dm_created1['dm_id'], "message": "Hi @ashnadesai this is a dm!"})

    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register2['token']})
    assert notifications.status_code == 200

    notification = notifications.json()
    assert notification == { 'notifications':
        [
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'jameshunt tagged you in ashnadesai, jameshunt, johndoe: Hi @ashnadesai this '},
        {
            'channel_id': -1,
            'dm_id': 1,
            'notification_message': 'jameshunt added you to ashnadesai, jameshunt, johndoe'},
        ]
    }

''' Tests for invalid token'''
def test_notifications_invalid_token(clear, register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
    notifications = requests.get(config.url + 'notifications/get/v1', params={"token": register1['token']})
    assert notifications.status_code == 403
