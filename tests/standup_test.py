import pytest

from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.channel import channel_join_v2
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src.standup import *
import time

from datetime import datetime

import requests
import json
from src import config



@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def new_user_1():
    response = requests.post (config.url+ 'auth/register/v2', json={"email" : "a@a.com", "password": "aaaaaaaa", "name_first" : "a", "name_last": "a"})
    register = response.json()
    return register

@pytest.fixture
def new_user_2():
    response2= requests.post(config.url+ 'auth/register/v2', json={"email" : "b@b.com", "password": "bbbbbbbb", "name_first" : "b", "name_last": "b"})
    register2 = response2.json()
    return register2

@pytest.fixture
def new_user_3():
    response = requests.post(config.url+ 'auth/register/v2', json={"email" : "c@c.com", "password": "ccccccccc", "name_first" : "c", "name_last": "c"})
    register = response.json()
    return register


@pytest.fixture
def channel_public(new_user_1):
    response3 = requests.post(config.url + 'channels/create/v2', json={"token": new_user_1['token'], "name" : "test", "is_public" : True })
    channel = response3.json()
    return channel

@pytest.fixture
def channel_public2(new_user_1):
    response3 = requests.post(config.url + 'channels/create/v2', json={"token": new_user_1['token'], "name" : "test", "is_public" : True })
    channel = response3.json()
    return channel

@pytest.fixture
def register0():
	""" Fixture that registers a valid user0 """
	response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	register0 = response.json()
	assert response.status_code == 200
	return register0

@pytest.fixture
def register1():
	""" Fixture that registers a valid user1 """
	response = requests.post(config.url + 'auth/register/v2', json={"email": "authenticemail@gmail.com", "password": "789ghj", "name_first": "Peter", "name_last": "Peters"})
	register1 = response.json()
	assert response.status_code == 200
	return register1

@pytest.fixture
def channel0(register0):
	""" Fixture that creates a channel0 """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	channel_create = response.json()
	assert response.status_code == 200
	return channel_create



''' Tests for standup_start'''
''' Test for valid output in standup_start'''
def test_standup_start_valid(clear, new_user_1, new_user_2):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id']})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_1["token"], "channel_id": channel["channel_id"], "length": 1})
    assert result.status_code == 200
    now = datetime.now()
    time_finish = int(now.strftime("%s")) + 1
    results = result.json()
    assert results['time_finish'] == time_finish


''' Test for invalid token in standup_start'''
def test_standup_start_invalid_token(clear, new_user_1):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_1["token"], "channel_id": channel["channel_id"] + 2, "length": 1})
    assert result.status_code == 403

''' Test for invalid channel in standup_start'''
def test_standup_start_invalid_channel(clear, new_user_1, new_user_2):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id']})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_1["token"], "channel_id": channel["channel_id"] + 2, "length": 1})
    assert result.status_code == 400

''' Test for invalid length in standup_start'''
def test_standup_start_invalid_length(clear, new_user_1, new_user_2):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id']})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_1["token"], "channel_id": channel["channel_id"], "length": -1})
    assert result.status_code == 400
    
''' Test for an active standup in standup_start'''
'''
def test_standup_start_invalid_length(clear, new_user_1, new_user_2, new_user_3):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_3['token'], "channel_id" : channel['channel_id']})
    requests.post(config.url + 'standup/start/v1', json={"token": new_user_1["token"], "channel_id": channel["channel_id"], "length": 1})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_3["token"], "channel_id": channel["channel_id"], "length": 1})
    assert result.status_code == 400
'''

''' Test for an user who is not a member of channel in standup_start'''
def test_standup_start_user_not_member(clear, new_user_1, new_user_2, new_user_3):
    channel = (requests.post(config.url + 'channels/create/v2', json={"token": new_user_1["token"], "name": "test", "is_public": True})).json()
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id']})
    result = requests.post(config.url + 'standup/start/v1', json={"token": new_user_3["token"], "channel_id": channel["channel_id"], "length": 1})
    assert result.status_code == 403

#Tests for Standup_Active

def test_standup_active_true(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """tests that standup active shows that a standup is active in a channel """
    a = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert a.status_code == 200
    response1 = requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public2['channel_id'], "length" : 10})
    start = response1.json()
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public['channel_id'], "length" : 10})

    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert response.status_code == 200
    is_active = response.json()
    assert is_active['is_active'] == True
    assert is_active['time_finish'] == start['time_finish']
    

def test_standup_active_false(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """tests that standup_active shows returns the correct values when a standup is not active"""
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public['channel_id'], "length" : 10})
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert response.status_code == 200
    is_active = response.json()
    assert is_active['is_active'] == False
    assert is_active['time_finish'] == None

def test_standup_active_false_2(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """tests that standup_active shows returns the correct values when a standup is not active"""
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public['channel_id'], "length" : 0})
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert response.status_code == 200
    is_active = response.json()
    assert is_active['is_active'] == False
    assert is_active['time_finish'] == None

def test_standup_active_invalid_token(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """test that standup_active returns an access error when the token is invalid"""
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public2['channel_id'], "length" : 10})
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_2['token']})
    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert response.status_code == 403
    

def test_standup_active_invalid_channel(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """tests that standup_active returns an input error when the channel_id is invalid"""
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public['channel_id'], "length" : 0})
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public2['channel_id'], "length" : 10})
    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']+1})
    assert response.status_code == 400
    

def test_standup_active_user_not_member(clear, new_user_1, new_user_2, channel_public, channel_public2):
    """tests that standup_active returns an access error when the user is not part of the channel"""
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public['channel_id'], "length" : 0})
    requests.post(config.url + 'standup/start/v1', json={"token" : new_user_1['token'], "channel_id": channel_public2['channel_id'], "length" : 10})
    response = requests.get(config.url + 'standup/active/v1', params={"token" : new_user_2['token'], 'channel_id' : channel_public2['channel_id']})
    assert response.status_code == 403
    



###### Standup - send ######

def test_standup_send_valid(clear, register0, channel0):
	""" Valid standup_send """
	requests.post(config.url + 'standup/start/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "length": 1})
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Standup!!!"})
	assert response0.status_code == 200

def test_standup_send_channel_id_invalid(clear, register0, channel0):
	""" Input exception - channel_id invalid """
	requests.post(config.url + 'standup/start/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "length": 1})
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"] + 7, "message": "Standup!!!"})
	assert response0.status_code == 400

def test_standup_send_message_length_greater_1000(clear, register0, channel0):
	""" Input exception - message length is greater than 1000 """
	requests.post(config.url + 'standup/start/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "length": 1})
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "H"*2441})
	assert response0.status_code == 400

'''
def test_standup_send_no_active_standup(clear, register0, channel0):
	""" Input exception - no active standup running """
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Standup!!!"})
	assert response0.status_code == 400
'''
def test_standup_send_valid_channel_invalid_member(clear, register0, register1, channel0):
	""" Access exception - member is sending a message to a channel they are not in """
	requests.post(config.url + 'standup/start/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "length": 1})
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register1["token"], "channel_id": channel0["channel_id"], "message": "Standup!!!"})
	assert response0.status_code == 403

def test_standup_send_invalid_token(clear, register0, channel0):
	""" Invalid token given """
	requests.post(config.url + 'standup/start/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "length": 1})
	response0 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Standup!!!"})
	assert response0.status_code == 200
	requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
	response1 = requests.post(config.url + 'standup/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Standup!!!"})
	assert response1.status_code == 403

