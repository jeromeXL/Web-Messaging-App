"""
tests for message functions
"""

import pytest 
from pylint import *
from src.channel import *
from src.other import *
from src.error import *
from src.channels import *
from src.auth import *
from src.data_store import *
from src.message import *
from src.dm import *
from src import config
import requests
import json
from datetime import *
import pytz


@pytest.fixture
def clear():
	""" Fixture that clears data_store before each test """
	test = requests.delete(config.url + 'clear/v1')
	assert test.status_code == 200

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
def register2():
	""" Fixture that registers a valid user1 """
	response = requests.post(config.url + 'auth/register/v2', json={"email": "prestigeemail@gmail.com", "password": "ovty678", "name_first": "Corey", "name_last": "Lazz"})
	register2 = response.json()
	assert response.status_code == 200
	return register2

@pytest.fixture
def channel_create(register0):
	""" Fixture that creates a channel_create """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	channel_create = response.json()
	assert response.status_code == 200
	return channel_create

@pytest.fixture
def channel_create1(register1):
	""" Fixture that creates a channel_create """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register1["token"], "name": "eurobeats", "is_public": True})
	channel_create = response.json()
	assert response.status_code == 200
	return channel_create

@pytest.fixture
def channel0(register0):
	""" Fixture that creates a channel0 """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	channel0 = response.json()
	assert response.status_code == 200
	return channel0

@pytest.fixture
def dm0(register0, register1):
	""" Fixture that creates a dm0 """
	response = requests.post(config.url + 'dm/create/v1', json={"token": register0["token"], "u_ids": [register1["auth_user_id"]]})
	dm0 = response.json()
	assert response.status_code == 200
	return dm0


@pytest.fixture
def dm1(register0, register1):
	""" Fixture that creates a dm0 """
	response = requests.post(config.url + 'dm/create/v1', json={"token": register0["token"], "u_ids": [register1["auth_user_id"]]})
	dm1 = response.json()
	assert response.status_code == 200
	return dm1


#Test message/send


''' Tests for message send'''


def test_message_send_v1():
	# send message 
	requests.delete(config.url + 'clear/v1')
	response0 =requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	response1 = response0.json()
	response2 = requests.post(config.url + 'auth/register/v2', json={"email": "authenticemail@gmail.com", "password": "789ghj", "name_first": "Peter", "name_last": "Peters"})
	response3 = response2.json()
	channel0 = requests.post(config.url + 'channels/create/v2', json={"token": response1["token"], "name": "eurobeat", "is_public": True})
	channel_id0 = channel0.json()
	requests.post(config.url + 'channel/join/v2', json={"token": response3['token'], "channel_id": channel_id0['channel_id']})
	response4 = requests.post(config.url + 'message/send/v1', json={"token": response1['token'], "channel_id": channel_id0['channel_id'], "message": "Hiiiiiii"})
	assert response4.status_code == 200
	response5 = requests.get(config.url + 'channel/messages/v2', params={"token": response1['token'], "channel_id": channel_id0['channel_id'], "start": 0})
	#response2 = response1.json()
	assert response5.status_code == 200
	#assert response1['messages'] == "Hiiiiiii"



'''' Invalid channel raises input error'''

def test_message_send_v1_invalid_channel_except(clear, register0, channel_create):
    # send message with invalid channel exception 
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"] + 2, "message": "Hiiiiiii"})
    assert response0.status_code == 400

''' Unauthorised user raises access error'''

def test_message_send_v1_unauthorised_user_except(clear, register2, channel_create):
    # send message with unauthorised user exception
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register2["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    print(response0)
    assert response0.status_code == 403

def test_message_send_v1_long_message_except(clear, register0, register1, channel_create):
	# send with long message exception 
	#requests.post(config.url + 'channel/join/v2', json={"token": register1['token'], "channel_id": channel_create['channel_id']})
	response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "H"*2389})
	assert response0.status_code == 400

def test_message_send_v1_invalid_token(clear, register0, channel_create):
    # invalid token error
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response1 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    assert response1.status_code == 403

# message_edit 


def test_message_edit_v1(clear, register0, channel_create):
    # edit message 
    #requests.post(config.url + 'channel/join/v2', json={"token": response3['token'], "channel_id": channel_id0['channel_id']})
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    requests.put(config.url + 'message/edit/v1', json={"token": register0["token"], "message_id": response1["message_id"], "message": "Byeeeeeee"})
    response3 = requests.get(config.url + 'channel/messages/v2', params={"token": register0['token'], "channel_id": channel_create['channel_id'], "start": 0})
    response4 = response3.json()
    assert response4["messages"][0].get("message") == "Byeeeeeee"


def test_message_edit_v1_unauthorised_user_except(clear, register0, register1, channel_create):
    # unauthorised user exception 
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response2 = requests.put(config.url + 'message/edit/v1', json={"token": register0["token"], "message_id": response1["message_id"], "message": "Byeeeeeee"})
    assert response2.status_code == 403


def test_message_edit_v1_long_message_except(clear, register0, channel_create):
    # long message exception 
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    response2 = requests.put(config.url + 'message/edit/v1', json={"token": register0["token"], "message_id": response1["message_id"], "message": "H"*2389})
    assert response2.status_code == 400

def test_message_edit_v1_valid_message_id_except_channel_id(clear, register0, register1, channel_create, channel_create1):
    # invalid channel_id but valid message_id
    #response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    #response1 = response0.json()
    response2 = requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel_create1["channel_id"], "message": "Heyyyyyy"})
    response3 = response2.json()
    response4 = requests.put(config.url + 'message/edit/v1', json={"token": register0["token"], "message_id": response3["message_id"] + 1, "message": "Byeeeeeee"})
    assert response4.status_code == 403

def test_message_edit_v1_channel_id_invalid_message_id_valid(clear, register0, register1, channel_create):
    # message_id_valid but not channel_id
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    response2 = requests.put(config.url + 'message/edit/v1', json={"token": register1["token"], "message_id": response1["message_id"] + 1, "message": "Byeeeeeee"})
    assert response2.status_code == 403

# message_remove 


def test_message_remove_v1(clear, register0, channel_create):
    # remove message
    send = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    message = send.json()
    requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel_create["channel_id"], "start": 0})
    requests.delete(config.url + 'message/remove/v1', json={"token": register0["token"], "message_id": message["message_id"]})
    response3 = requests.get(config.url + 'channel/messages/v2', params={"token": register0['token'], "channel_id": channel_create['channel_id'], "start": 0})
    response4 = response3.json()
    assert response3.status_code == 200
    assert len(response4["messages"]) == 0



def test_message_remove_v1_unauthorised_user_except(clear, register0, register1, channel_create):
    # remove message with unauthorised user exception
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response2 = requests.delete(config.url + 'message/remove/v1', json={"token": register0["token"], "message_id": response1["message_id"]})
    assert response2.status_code == 403

def test_message_remove_v1_message_id_valid_channel_invalid(clear, register0, register1, channel_create):
    # invalid channel_id but valid message_id
    response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    response1 = response0.json()
    response2 = requests.delete(config.url + 'message/remove/v1', json={"token": register1["token"], "message_id": response1["message_id"] + 1})
    assert response2.status_code == 403
    
def test_message_remove_v1_valid_message_id_but_not_channel(clear, register0, register1, channel_create, channel_create1):
    # message_id but not channel_id
    #response0 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    #response1 = response0.json()
    response2 = requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel_create1["channel_id"], "message": "Heyyyyyy"})
    response3 = response2.json()
    response4 = requests.delete(config.url + 'message/remove/v1', json={"token": register0["token"], "message_id": response3["message_id"] + 1})
    assert response4.status_code == 403



# message_senddm 
def test_message_senddm_valid(clear, register0, register1, channel_create, dm0):
    # senddm valid
    response0 = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Hiiiiiii"})
    assert response0.status_code == 200

def test_message_senddm_v1_invalid_channel_except(clear, register0, register1, channel_create, dm0):
    # send dm with invalid dm exception
    response0 = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": "dm456", "message": "Hiiiiiii"})
    assert response0.status_code == 400

def test_message_senddm_v1_long_message_except(clear, register0, channel_create, dm0):
    # send dm with long message exception
    response0 = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": "dm890", "message": "H"*2389})
    assert response0.status_code == 400

def test_message_senddm_v1_token_invalid(clear, register0, register1, channel_create, dm0):
    # token invalid
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response0 = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Hiiiiiii"})
    assert response0.status_code == 403
    
def test_message_senddm_v1_dm_id_valid_dm_invalid_member(clear, register0, register1, register2, dm0):
    # invalid dm member but valid dm_id
    response0 = requests.post(config.url + 'message/senddm/v1', json={"token": register2["token"], "dm_id": dm0["dm_id"], "message": "Hiiiiiii"})
    assert response0.status_code == 403


#message_react

def test_message_react_success(clear, register0, register1, register2, channel_create, channel_create1, dm0, dm1):
    """ react is successful in multiple channels and dms"""

    #make users join channels
    requests.post(config.url+'channel/join/v2', json={"token" : register1['token'], "channel_id" : channel_create['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel_create['channel_id']})
    requests.post(config.url+'channel/join/v2', json={"token" : register0['token'], "channel_id" : channel_create1['channel_id']})
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel_create1['channel_id']})
    

    #send messages in channel1
    a = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "Hiiiiiii"})
    message = a.json()
    requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel_create["channel_id"], "message": "Hello"})
    c = requests.post(config.url + 'message/send/v1', json={"token": register1["token"], "channel_id": channel_create["channel_id"], "message": "bonjour"})
    message2 = c.json()

    #send messages in channel2
    requests.post(config.url + 'message/send/v1', json={"token": register2["token"], "channel_id": channel_create1["channel_id"], "message": "bonjour"})
    e = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create1["channel_id"], "message": "bonjour"})
    message3 = e.json()
    
    #send messages in dm1
    requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    f = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message4 = f.json()

    #send messages in dm2
    requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm1['dm_id'], "message": "H"})
    g = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm1['dm_id'], "message": "H"})
    message5 = g.json()

    #react to messages
    response = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message["message_id"], "react_id" : 1})
    assert response.status_code == 200
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], "message_id" : message["message_id"], "react_id" : 1})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], 'message_id' : message2['message_id'], 'react_id' : 1 })
    assert response3.status_code == 200
    response4 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], 'message_id' : message3['message_id'], 'react_id' : 1})
    assert response4.status_code == 200
    response7 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], 'message_id' : message4['message_id'], 'react_id' : 1})
    assert response7.status_code == 200
    response8 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], 'message_id' : message5['message_id'], 'react_id' : 1})
    assert response8.status_code == 200
    
    response5 = requests.get(config.url + 'channel/messages/v2', params={"token" : register1['token'], 'channel_id' : channel_create['channel_id'], 'start' : 0})
    channel_messages = response5.json()
    assert channel_messages['messages'][2]['reacts'][0]['u_ids'] == [register1['auth_user_id'], register2['auth_user_id']]
    assert channel_messages['messages'][0]['reacts'][0]['u_ids'] == [register2['auth_user_id']]
    assert channel_messages['messages'][2]['reacts'][0]['is_this_user_reacted'] == True
    assert channel_messages['messages'][0]['reacts'][0]['is_this_user_reacted'] == False
    response6 = requests.get(config.url + 'channel/messages/v2', params={"token" : register0['token'], 'channel_id' : channel_create1['channel_id'], 'start' : 0})
    channel_messages2 = response6.json()
    print(channel_messages2)
    assert channel_messages2['messages'][0]['reacts'][0]['u_ids'] == [register1['auth_user_id']]
    response9  = requests.get(config.url + 'dm/messages/v1', params={"token" : register1['token'], "dm_id" : dm0['dm_id'], 'start' : 0})
    assert response9.status_code == 200
    dm_messages = response9.json()
    assert dm_messages['messages'][0]['reacts'][0]['u_ids'] == [register1['auth_user_id']]
    assert dm_messages['messages'][1]['reacts'][0]['is_this_user_reacted'] == False
    assert dm_messages['messages'][0]['reacts'][0]['is_this_user_reacted'] == True
    response10 = requests.get(config.url + 'dm/messages/v1', params={"token" : register1['token'], "dm_id" : dm1['dm_id'], 'start' : 0})
    assert response10.status_code == 200
    dm_messages2 = response10.json()
    assert dm_messages2['messages'][0]['reacts'][0]['u_ids']==[register1['auth_user_id']]
    


def test_message_react_invalid_token(clear, register0, register1, register2, dm0):
    """error is raised when an invalid token is passed """
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 403
    

def test_message_react_invalid_message_id(clear, register0, register1, register2, dm0):
    """error is raised when an invalid message_id is passed"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id']+1, "react_id" : 1})
    assert response2.status_code == 400
    

def test_message_react_invalid_react_id(clear, register0, register1, register2, dm0):
    """error is raised when an invalid react_id is passed"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 900})
    assert response2.status_code == 400
    

def test_message_react_already_contains_react_from_auth_user(clear, register0, register1, register2, dm0, channel_create):
    """error is raised when the message already contains a react from the auth_user"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response3.status_code == 400
    response4 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "bonjour"})
    message2 = response4.json()
    response5 = requests.post(config.url + 'message/react/v1', json={"token" : register0['token'], "message_id" : message2['message_id'], "react_id" : 1})
    assert response5.status_code == 200
    response6 = requests.post(config.url + 'message/react/v1', json={"token" : register0['token'], "message_id" : message2['message_id'], "react_id" : 1})
    assert response6.status_code == 400


    

#Tests for message unreact
def test_message_unreact_success(clear, register0, register1, register2, channel_create, channel_create1, dm0, dm1):
    """message unreact is successful for all dms and channels"""
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : channel_create1['channel_id']})
    requests.post(config.url + 'message/send/v1', json={"token" : register1["token"], "channel_id" : channel_create1['channel_id'], "message" : "hii"})
    response = requests.post(config.url + 'message/send/v1', json={"token" : register1["token"], "channel_id" : channel_create1['channel_id'], "message" : "hii"})
    message = response.json()
    requests.post(config.url + 'message/senddm/v1', json={"token" : register1["token"], "dm_id" : dm1['dm_id'], "message" : "hii"})
    response2 = requests.post(config.url + 'message/senddm/v1', json={"token" : register1["token"], "dm_id" : dm1['dm_id'], "message" : "hii"})
    message2 = response2.json()
    requests.post(config.url + 'message/react/v1', json={"token" : register2['token'], "message_id" : message['message_id'], "react_id" : 1})
    requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message2['message_id'], "react_id" : 1})
    response3 = requests.post(config.url + 'message/unreact/v1', json={"token" : register2['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response3.status_code == 200
    response4 = requests.post(config.url + 'message/unreact/v1', json={"token" : register1['token'], "message_id" : message2['message_id'], "react_id" : 1})
    assert response4.status_code == 200
    response5 = requests.get(config.url + 'channel/messages/v2', params={"token" : register2['token'], 'channel_id' : channel_create1['channel_id'], 'start' : 0})
    channel_messages = response5.json()
    assert channel_messages['messages'][1]['reacts'][0]['is_this_user_reacted'] == False
    response6  = requests.get(config.url + 'dm/messages/v1', params={"token" : register1['token'], "dm_id" : dm1['dm_id'], 'start' : 0})
    dm_messages = response6.json()
    assert dm_messages['messages'][1]['reacts'][0]['is_this_user_reacted'] == False



def test_message_unreact_token_invalid(clear, register0, register1, dm0):
    """tests that an error is raised when the token is invalid"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 200
    requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
    response3 = requests.post(config.url + 'message/unreact/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response3.status_code == 403

def test_message_unreact_invalid_message_id(clear, register0, register1, dm0):
    """tests that an error is raised when message ID is not valid for the user"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/unreact/v1', json={"token" : register1['token'], "message_id" : message['message_id']+1, "react_id" : 1})
    assert response3.status_code == 400
    

def test_message_unreact_invalid_react_id(clear, register0, register1, dm0):
    """tests that an error is raised when an invalid react ID is passed"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/react/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/unreact/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 900})
    assert response3.status_code == 400

def test_message_unreact_message_not_reacted(clear, register0, register1, dm0, channel_create):
    """tests that an error is raised when the user tries to unreact a message they haven't reacted to"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/unreact/v1', json={"token" : register1['token'], "message_id" : message['message_id'], "react_id" : 1})
    assert response2.status_code == 400
    response3 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "bonjour"})
    message2 = response3.json()
    response4 = requests.post(config.url + 'message/unreact/v1', json={"token" : register0['token'], "message_id" : message2['message_id'], "react_id" : 1})
    assert response4.status_code == 400



''' Tests for function message_share '''

''' Tests that an error is raised when the token is invalid '''
def test_message_share_token_invalid(clear, register0, channel_create):
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel_create['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": channel2['channel_id'], 
                                                                        "dm_id": -1})
    assert response2.status_code == 403

''' Tests that an error is raised when both channel_id and dm_id are invalid '''
def test_message_share_channel_dm_invalid(clear, register0, channel_create):
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel_create['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": -1, 
                                                                        "dm_id": -1})
    assert response2.status_code == 400

''' Tests that an error is raised when neither channel_id nor dm_id are -1 '''
def test_message_share_channel_and_dm_valid(clear, register0, channel_create, dm0):
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel_create['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": channel2['channel_id'], 
                                                                        "dm_id": dm0['dm_id']})
    assert response2.status_code == 400

''' Tests that an error is raised when an invalid message is shared '''
def test_message_share_message_invalid(clear, register0, channel_create):
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": 1, 
                                                                        "message": 'Hello', 
                                                                        "channel_id": channel2['channel_id'], 
                                                                        "dm_id": -1})
    assert response2.status_code == 400

''' Tests that an error is rasied when the length of the message is more than 1000 characters '''
def test_message_share_message_too_long(clear, register0, channel_create, dm0):
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel_create['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    message_shared = 'hello'
    message_shared = message_shared * 300
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": message_shared, 
                                                                        "channel_id": channel2['channel_id'], 
                                                                        "dm_id": -1})
    assert response2.status_code == 400

''' Tests that an error is raised when user not a member if the channel they are sharing too '''
def test_message_share_user_not_in_channel(clear, register0, register2, channel_create):
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel_create['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register2["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": channel2['channel_id'], 
                                                                        "dm_id": -1})
    assert response2.status_code == 403

''' Tests that an error is raised when user not a member if the dm they are sharing too '''
def test_message_share_user_not_in_dm(clear, register0, register1, register2, dm0):
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0['token'], "dm_id": dm0['dm_id'], "message": "Hiiiiiii"})
    message = response.json()
    response1 = requests.post(config.url + 'dm/create/v1', json={"token": register2["token"], "u_ids": [register1["auth_user_id"]]})
    dm2 = response1.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": -1, 
                                                                        "dm_id": dm2['dm_id']})
    assert response2.status_code == 403

''' Tests that a valid output is given when a message from a channel is shared to a dm '''
def test_message_share_valid_channel_to_dm(clear, register0, channel_create, dm0):
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "test", "is_public": True})
    channel2 = response1.json()
    requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel2['channel_id'], "message": "Hi there"})
    response = requests.post(config.url + 'message/send/v1', json={"token": register0['token'], "channel_id": channel2['channel_id'], "message": "Hiiiiiii"})
    message = response.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": 'Hello', 
                                                                        "channel_id": -1, 
                                                                        "dm_id": dm0['dm_id']})
    shared_message = response2.json()
    assert response2.status_code == 200
    assert shared_message['shared_message_id'] != message['message_id']
    response3 = requests.get(config.url + 'dm/messages/v1', params={"token": register0['token'], "dm_id": dm0['dm_id'], "start": 0})
    dm_messages = response3.json()
    assert 'Hello' in dm_messages['messages'][0]['message']

''' Tests that a valid output is given when a message from a dm is shared to a channel '''
def test_message_share_valid_dm_to_channel(clear, register0, register2, channel_create, dm0):
    response1 = requests.post(config.url + 'dm/create/v1', json={"token": register0["token"], "u_ids": [register2["auth_user_id"]]})
    dm2 = response1.json()
    requests.post(config.url + 'message/senddm/v1', json={"token": register0['token'], "dm_id": dm2['dm_id'], "message": "Hi there"})
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0['token'], "dm_id": dm2['dm_id'], "message": "Hiiiiiii"})
    message = response.json()
    response2 = requests.post(config.url + 'message/share/v1', json={"token": register0['token'], 
                                                                        "og_message_id": message['message_id'], 
                                                                        "message": '', 
                                                                        "channel_id": channel_create['channel_id'], 
                                                                        "dm_id": -1})
    shared_message = response2.json()
    assert response2.status_code == 200
    assert shared_message['shared_message_id'] != message['message_id']
    

#tests for message pin 

def test_message_pin_invalid_token(clear, register0, register1, register2, dm0):
    """error is raised when an invalid token is passed """
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 403
    

def test_message_pin_invalid_message_id(clear, register0, register1, register2, dm0):
    """error is raised when an invalid message_id is passed"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']+1})
    assert response2.status_code == 400

def test_message_pin_already_pinned(clear, register0, register1, register2, dm0, channel_create):
    """error is raised when the message is already pinned"""
    #dm
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response3.status_code == 400
    #channel
    response4 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "bonjour"})
    message2 = response4.json()
    response5 = requests.post(config.url + 'message/pin/v1', json={"token" : register0['token'], "message_id" : message2['message_id']})
    assert response5.status_code == 200
    response6 = requests.post(config.url + 'message/pin/v1', json={"token" : register0['token'], "message_id" : message2['message_id']})
    assert response6.status_code == 400
    
    
# tests for message unpin

def test_message_unpin_token_invalid(clear, register0, register1, dm0):
    """tests that an error is raised when the token is invalid"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 200
    requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
    response3 = requests.post(config.url + 'message/unpin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response3.status_code == 403

def test_message_unpin_invalid_message_id(clear, register0, register1, dm0):
    """tests that an error is raised when message ID is not valid for the user"""
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/unpin/v1', json={"token" : register1['token'], "message_id" : message['message_id']+1})
    assert response3.status_code == 400

def test_message_unpin_message_not_pinned(clear, register0, register1, dm0, channel_create):
    """tests that an error is raised when the user tries to unreact a message they haven't reacted to"""
    #dm
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/unpin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 400
    #channel
    response3 = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel_create["channel_id"], "message": "bonjour"})
    message2 = response3.json()
    response4 = requests.post(config.url + 'message/unpin/v1', json={"token" : register0['token'], "message_id" : message2['message_id']})
    assert response4.status_code == 400
    
def test_message_unpin_valid_dm(clear, register0, register1, dm0):
    ''' Tests no error is raised when valid inputs are given for a dm '''
    response = requests.post(config.url + 'message/senddm/v1', json={"token": register0["token"], "dm_id": dm0['dm_id'], "message": "H"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/unpin/v1', json={"token" : register1['token'], "message_id" : message['message_id']})
    assert response3.status_code == 200

def test_message_unpin_valid_channel(clear, register0, channel0):
    ''' Tests no error is raised when valid inputs are given for a channel '''
    requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0['channel_id'], "message": "H"})
    response = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0['channel_id'], "message": "E"})
    message = response.json()
    response2 = requests.post(config.url + 'message/pin/v1', json={"token" : register0['token'], "message_id" : message['message_id']})
    assert response2.status_code == 200
    response3 = requests.post(config.url + 'message/unpin/v1', json={"token" : register0['token'], "message_id" : message['message_id']})
    assert response3.status_code == 200
    
###### Message - sendlater ######

def test_message_sendlater_valid(clear, register0, channel0):
	""" Valid message_sendlater """
	time_elapsed = 6
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 200
	response1 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you real soon", "time_sent": config_time + time_elapsed})
	assert response1.status_code == 200

def test_message_sendlater_valid_tagging(clear, register0, channel0):
	""" Valid message_sendlater containing tagging """
	time_elapsed = 6
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later@jameshunt", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 200

def test_message_sendlater_channel_id_invalid(clear, register0, channel0):
	""" Input exception - channel_id invalid """
	time_elapsed = 3
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"] + 3, "message": "Talk to you real soon", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlater_message_length_less_0(clear, register0, channel0):
	""" Input exception - message length is below 0 """
	time_elapsed = 4
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlater_message_length_greater_1000(clear, register0, channel0):
	""" Input exception - message length is greater than 1000 """
	time_elapsed = 5
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "H"*2441, "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlater_time_sent_is_past(clear, register0, channel0):
	""" Input exception - message sent has a time that has passed """
	time_elapsed = 20
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you real soon", "time_sent": config_time - time_elapsed})
	assert response0.status_code == 400

def test_message_sendlater_valid_channel_invalid_member(clear, register0, register1, channel0):
	""" Access exception - member is sending a message to a channel they are not in """
	time_elapsed = 7
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlater/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlater/v1', json={"token": register1["token"], "channel_id": channel0["channel_id"], "message": "Talk to you now", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 403



###### Message - sendlaterdm ######

def test_message_sendlaterdm_valid(clear, register0, register1, dm0):
	""" Valid message_sendlaterdm """
	time_elapsed = 6
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 200
	response1 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you real soon", "time_sent": config_time + time_elapsed})
	assert response1.status_code == 200

def test_message_sendlaterdm_valid_tagging(clear, register0, register1, dm0):
	""" Valid message_sendlaterdm with tagging """
	time_elapsed = 6
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later@jameshunt", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 200

def test_message_sendlaterdm_channel_id_invalid(clear, register0, register1, dm0):
	""" Input exception - dm_id invalid """
	time_elapsed = 3
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"] + 5, "message": "Talk to you real soon", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlaterdm_message_length_less_0(clear, register0, register1, dm0):
	""" Input exception - message length is below 0 """
	time_elapsed = 4
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlaterdm_message_length_greater_1000(clear, register0, register1, dm0):
	""" Input exception - message length is greater than 1000 """
	time_elapsed = 5
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "H"*2441, "time_sent": config_time + time_elapsed})
	assert response0.status_code == 400

def test_message_sendlaterdm_time_sent_is_past(clear, register0, register1, dm0):
	""" Input exception - message sent has a time that has passed """
	time_elapsed = 20
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you real soon", "time_sent": config_time - time_elapsed})
	assert response0.status_code == 400

def test_message_sendlaterdm_valid_channel_invalid_member(clear, register0, register1, register2, dm0):
	""" Access exception - member is sending a message to a dm they are not in """
	time_elapsed = 7
	config_time = datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
	requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register0["token"], "dm_id": dm0["dm_id"], "message": "Talk to you later", "time_sent": config_time + time_elapsed})
	response0 = requests.post(config.url + 'message/sendlaterdm/v1', json={"token": register2["token"], "dm_id": dm0["dm_id"], "message": "Talk to you now", "time_sent": config_time + time_elapsed})
	assert response0.status_code == 403
