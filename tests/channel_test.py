''' 
Test cases for channel.py which contains functions channel_invite_v1, channel_details_v1, channel_messages_v1 and channel_join_v1
'''

import pytest 
from pylint import *
from src.channel import *
from src.other import *
from src.error import *
from src.channels import *
from src.auth import *
from src.data_store import *
from src import config
import requests
import json

''' FIXTURES '''

''' Fixture that clears data_store and registers a valid user '''
@pytest.fixture
def clear_and_register1():
    requests.delete(config.url + 'clear/v1')
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register1 = response.json()
    return register1


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
def channel_public(new_user_1):
    response3 = requests.post(config.url + 'channels/create/v2', json={"token": new_user_1['token'], "name" : "test", "is_public" : True })
    channel = response3.json()
    return channel

@pytest.fixture
def channel_private(new_user_1):
    response = requests.post(config.url + 'channels/create/v2', json={"token": new_user_1['token'], "name" : "test", "is_public" : False})
    channel = response.json()
    return channel

@pytest.fixture 
def creates_channel(clear_and_register1):
    response = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "Jerome", "is_public": True})
    channel1 = response.json()
    return channel1

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
def register1():
	""" Fixture that registers a valid user1 """
	response = requests.post(config.url + 'auth/register/v2', json={"email": "authenticemail@gmail.com", "password": "789ghj", "name_first": "Peter", "name_last": "Peters"})
	register1 = response.json()
	return register1


@pytest.fixture
def channel0(register0):
	""" Fixture that creates a channel0 """
	response = requests.post(config.url + 'channels/create/v2', json={"token": register0["token"], "name": "eurobeat", "is_public": True})
	channel0 = response.json()
	return channel0

''' CHANNEL_DETAILS TESTS '''

# Channel Details Valid Test For One Member
def test_details_valid_one_member(clear_and_register1):
    """ details with valid one member """
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1['token'], "name": "test", "is_public": True})
    channel = response1.json()
    response2 = requests.get(config.url + 'channel/details/v2', params={"token": clear_and_register1['token'], "channel_id": channel['channel_id']})
    details = response2.json()
    assert response2.status_code == 200
    correct_details = {'name': 'test',
        'is_public': True,
        'owner_members': [
            {
                'u_id': clear_and_register1['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'James',
                'name_last': 'Hunt',
                'handle_str': 'jameshunt',
            }
        ],
        'all_members': [
            {
                'u_id': clear_and_register1['auth_user_id'],
                'email': 'validemail@gmail.com',
                'name_first': 'James',
                'name_last': 'Hunt',
                'handle_str': 'jameshunt',
            }
        ],
     }

    assert details == correct_details


# Channel Details Valid Test for Two Members
def test_details_valid_two_members(clear, new_user_2, new_user_1, channel_public):    
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']})
    response5 = requests.get(config.url + 'channel/details/v2', params={"token": new_user_2['token'], "channel_id" : channel_public['channel_id']})
    details = response5.json()
    correct_details = {'name': 'test',
        'is_public': True,
        'owner_members': [
            {
                'u_id': new_user_1['auth_user_id'],
                'email': 'a@a.com',
                'name_first': 'a',
                'name_last': 'a',
                'handle_str': 'aa',
            }
        ],
        'all_members': [
            {
                'u_id': new_user_1['auth_user_id'],
                'email': 'a@a.com',
                'name_first': 'a',
                'name_last': 'a',
                'handle_str': 'aa',
            },
            {
                'u_id': new_user_2['auth_user_id'],
                'email': 'b@b.com',
                'name_first': 'b',
                'name_last': 'b',
                'handle_str': 'bb',
            }
        ]
     }

    assert details == correct_details

# Raises Input Error if channel_id is not valid
def test_details_input_fail(clear_and_register1):
    """ details with input fail """
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1['token'], "name": "test2", "is_public": True})
    channel = response1.json()
    response2 = requests.get(config.url + 'channel/details/v2', params={"token": clear_and_register1['token'], "channel_id": channel['channel_id'] + 3})
    assert response2.status_code == 400

# Raises Access Error if User is not a member of channel
def test_details_access_fail(clear_and_register1):
    """ details with access_fail """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234abcd", "name_first": "James2", "name_last": "Hunt2"})
    register1 = response.json()
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1['token'], "name": "test", "is_public": True})
    channel = response1.json()
    response2 = requests.get(config.url + 'channel/details/v2', params={"token": register1['token'], "channel_id": channel['channel_id']})
    assert response2.status_code == 403

# Raises Access Error for Invalid Token
def tests_details_invalid_token(clear_and_register1, creates_channel):
    """ remove with invalid token """
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.get(config.url + 'channel/details/v2', params={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"]})
    assert response1.status_code == 403

#tests for channel_join_v1

def test_join_authorized_user(clear, new_user_2, new_user_1, channel_public):    
    response4 = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']})
    assert response4.status_code == 200
    response5 = requests.get(config.url + 'channel/details/v2', params={"token": new_user_2['token'], "channel_id" : channel_public['channel_id']})
    details = response5.json() 
    details2 = details['owner_members'][0]['u_id']
    assert(new_user_1['auth_user_id'] == details2)

def test_join_unauthorized_user(clear, new_user_1, channel_public):
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    response = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id']})

    assert response.status_code == 403


def test_join_invalid_channel_id(clear, new_user_2, channel_public):
    response = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']+1})
    assert response.status_code == 400
   
def test_join_user_already_member(clear, new_user_1, channel_public):
    response = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id']})
    assert response.status_code == 400

   
def test_join_private_channel_pass(clear, new_user_1, new_user_2 ):
    response = requests.post(config.url + 'channels/create/v2', json={"token" : new_user_2['token'], "name" : "test", "is_public" : False })
    private_channel = response.json()
    response2 = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_1['token'], "channel_id" : private_channel['channel_id']})
    assert response2.status_code == 200
    response3 = requests.get(config.url + 'channel/details/v2', params={"token": new_user_2['token'], "channel_id" : private_channel['channel_id']})
    details = response3.json()
    assert (details['owner_members'][0]['u_id'] == new_user_2['auth_user_id'])

    
   

def test_join_private_channel_fail(clear, new_user_1, new_user_2, channel_private):
    response = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : channel_private['channel_id']})
    assert response.status_code == 403




#tests for channel_invite_v1

def test_invite_public(clear, new_user_1, new_user_2, channel_public):
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
    response2 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']})
    details = response2.json()
    assert (details['owner_members'][0]['u_id'] == new_user_1['auth_user_id'])

 
def test_invite_private(clear, new_user_1, new_user_2, channel_private):
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_private['channel_id'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
    response2 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2['token'], "channel_id" : channel_private['channel_id']})
    assert response2.status_code == 200
    details = response2.json()
    assert(details['owner_members'][0]['u_id'] == new_user_1['auth_user_id'])


def test_invite_invalid_channel(clear, new_user_1, new_user_2, channel_public):
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id']+1, "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 400

   
def test_invite_invalid_u_id(clear, new_user_1, new_user_2, channel_public):
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_2['auth_user_id']+1})
    assert response.status_code == 400


def test_invite_already_member(clear, new_user_1, new_user_2, channel_public):
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
    response2 = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_2['auth_user_id']})
    assert response2.status_code == 400

def test_invite_auth_not_member(clear, new_user_1, new_user_2):
    response = requests.post(config.url + 'auth/register/v2', json={"email" : "c@c.com", "password": "cccccccc", "name_first" : "c", "name_last": "c"})
    user3 = response.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email" : "d@d.com", "password": "dddddddd", "name_first" : "d", "name_last": "d"})
    assert response2.status_code == 200
    user4 = response2.json()
    response3 = requests.post(config.url + 'channels/create/v2', json={"token" : new_user_2['token'], "name" : "test", "is_public" : True })
    channel = response3.json()
    response4 = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_2['token'], "channel_id" : channel['channel_id'], "u_id" : user3['auth_user_id']})
    assert response4.status_code == 200
    response5 = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel['channel_id'], "u_id" : user4["auth_user_id"] })
    assert response5.status_code == 403

def test_invite_invalid_token(clear, new_user_1, channel_public):
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    response = requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_1["auth_user_id"] })
    assert response.status_code == 403






def test_leave_token_invalid(clear_and_register1, creates_channel):
    """ leave with token invalid """
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.post(config.url + 'channel/leave/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"]})
    assert response1.status_code == 403

def test_leave_channel_id_invalid(clear_and_register1, creates_channel):
    """ leave with channel invalid id"""
    response1 = requests.post(config.url + 'channel/leave/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"] + 1})
    assert response1.status_code == 400

def test_leave_user_not_channel(clear_and_register1, creates_channel):
    """ leave with user not in the channel """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response1 = requests.post(config.url + 'channel/leave/v1', json={"token": register2["token"], "channel_id": creates_channel["channel_id"]})
    assert response1.status_code == 403
    
def test_leave_valid(clear_and_register1, creates_channel):
    """ valid leave """
    response1 = requests.post(config.url + 'channel/leave/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"]})
    leave = response1.json()
    assert response1.status_code == 200
    assert leave == {}

def test_list_after_leave_channel(clear_and_register1, creates_channel, new_user_2):
    requests.post(config.url + 'channel/invite/v2', json={"token" : clear_and_register1['token'], "channel_id" : creates_channel['channel_id'], "u_id" : new_user_2['auth_user_id']})
    response1 = requests.post(config.url + 'channel/leave/v1', json={"token": new_user_2["token"], "channel_id": creates_channel["channel_id"]})
    assert response1.status_code == 200
    response2 = requests.get(config.url + 'channels/list/v2', params={"token" : new_user_2['token']})
    list = response2.json()
    assert list['channels'] == []

### Tests for channel_addowner
def test_add_token_invalid(clear_and_register1, creates_channel):
    """ add with token invalid """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    assert response1.status_code == 403

def test_add_channel_id_invalid(clear_and_register1, creates_channel):
    """ add with channel invalid id """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"] + 1, "u_id": register2["auth_user_id"]})
    assert response1.status_code == 400

def test_add_no_channels_exit(clear_and_register1):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": -1, "u_id": register2["auth_user_id"]})
    assert response1.status_code == 400
def test_add_uid_invalid(clear_and_register1, creates_channel):
    """ add with invalid u_id"""
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"] + clear_and_register1["auth_user_id"]})
    assert response1.status_code == 400

def test_add_uid_not_channel(clear_and_register1, creates_channel):
    """ add with u_id not in the channel """
    requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    response3 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register3 = response3.json()
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register3["auth_user_id"]})
    assert response1.status_code == 400

def test_add_uid_already_owner(clear_and_register1, creates_channel):
    """ add with u_id of already an owner """
    requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": clear_and_register1["auth_user_id"]})
    assert response1.status_code == 400

def test_add_no_owner_permissions(clear_and_register1, creates_channel):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response3 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register3 = response3.json()
    requests.post(config.url + 'channel/join/v2', json={"token": register2["token"], "channel_id" : creates_channel['channel_id']})
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": register2["token"], "channel_id": creates_channel["channel_id"], "u_id": register3["auth_user_id"]})
    assert response1.status_code == 403


def test_add_valid(clear_and_register1, creates_channel):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/join/v2', json={"token" : register2['token'], "channel_id" : creates_channel["channel_id"] })
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    output = response1.json()
    assert output == {}
    assert response1.status_code == 200
    response3 = requests.get(config.url + 'channel/details/v2', params={"token" : register2["token"], "channel_id" : creates_channel['channel_id']})
    details = response3.json()
    assert register2['auth_user_id'] in [k['u_id'] for k in details['owner_members']]

def test_global_owner_can_add_member(clear_and_register1, new_user_1, new_user_2, creates_channel):
    a = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_1['token'], "channel_id" : creates_channel["channel_id"] })
    assert a.status_code == 200
    b = requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : creates_channel["channel_id"] })
    assert b.status_code == 200
    c = requests.post(config.url + 'admin/userpermission/change/v1', json={"token" : clear_and_register1['token'], "u_id" : new_user_1['auth_user_id'], 'permission_id' : 1})
    assert c.status_code == 200
    response1 = requests.post(config.url + 'channel/addowner/v1', json={"token": new_user_1["token"], "channel_id": creates_channel["channel_id"], "u_id": new_user_2["auth_user_id"]})
    assert response1.status_code == 200
    response3 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2["token"], "channel_id" : creates_channel['channel_id']})
    details = response3.json()
    assert new_user_2['auth_user_id'] in [k['u_id'] for k in details['owner_members']]


## Tests for channel_removeowner

def test_remove_token_invalid(clear_and_register1, creates_channel):
    """ remove with invalid token """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    assert response1.status_code == 403

def test_remove_invalid_user(clear_and_register1, creates_channel):
    """ remove with an invalid user """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"] + 789})
    assert response1.status_code == 400

def test_remove_invalid_owner(clear_and_register1, creates_channel):
    """ remove with an invalid owner """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    assert response1.status_code == 400

def test_remove_only_owner(clear_and_register1, creates_channel):
    """ remove with only owner """
    requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": clear_and_register1["auth_user_id"]})
    assert response1.status_code == 400

def test_remove_no_owner_permissions(clear_and_register1, creates_channel):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    assert response1.status_code == 403


def test_remove_valid(clear_and_register1, creates_channel):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/join/v2', json={"token": register2["token"], "channel_id" : creates_channel['channel_id']})

    requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    response2 = requests.post(config.url + 'channel/removeowner/v1', json={"token": register2["token"], "channel_id": creates_channel["channel_id"], "u_id": clear_and_register1["auth_user_id"]})
    assert response2.status_code == 200
    

def test_remove_channel_id_invalid(clear_and_register1, creates_channel):
    """ remove with invalid channel_id """
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    requests.post(config.url + 'channel/addowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"], "u_id": register2["auth_user_id"]})
    response1 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": creates_channel["channel_id"] + 2323, "u_id": register2["auth_user_id"]})
    assert response1.status_code == 400

def test_global_owner_can_remove_owner(clear_and_register1, creates_channel, new_user_1, new_user_2):
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_1['token'], "channel_id" : creates_channel["channel_id"] })
    requests.post(config.url + 'channel/join/v2', json={"token" : new_user_2['token'], "channel_id" : creates_channel["channel_id"] })
    requests.post(config.url + 'admin/userpermission/change/v1', json={"token" : clear_and_register1['token'], "u_id" : new_user_1['auth_user_id'], 'permission_id' : 1})
    requests.post(config.url + 'channel/addowner/v1', json={"token": new_user_1["token"], "channel_id": creates_channel["channel_id"], "u_id": new_user_2["auth_user_id"]})
    requests.post(config.url + 'channel/removeowner/v1', json={"token": new_user_1["token"], "channel_id": creates_channel["channel_id"], "u_id": new_user_2["auth_user_id"]})
    response3 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2["token"], "channel_id" : creates_channel['channel_id']})
    details = response3.json()
    assert new_user_2['auth_user_id'] not in [k['u_id'] for k in details['owner_members']]
# channel_messages_v2

def test_global_owner_cannot_remove_only_onwer(clear_and_register1, new_user_1, ):
    response = requests.post(config.url + 'channels/create/v2', json={"token": new_user_1['token'], "name" : "test", "is_public" : True })
    channel = response.json()
    requests.post(config.url + 'channel/join/v2', json={"token" : clear_and_register1['token'], "channel_id" : channel["channel_id"] })
    response2 = requests.post(config.url + 'channel/removeowner/v1', json={"token": clear_and_register1["token"], "channel_id": channel["channel_id"], "u_id": new_user_1["auth_user_id"]})
    assert response2.status_code == 400




""" Tests for channel_messages """

def test_channel_messages_exception(clear, register0, register1, channel0):
	# test channel messages with exception unauthorised user
    requests.post(config.url + 'auth/logout/v1', json={"token": register0['token']})
    response0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 0})
    assert response0.status_code == 403

def test_channel_messages_user_not_in_channel(clear, register0, register1, channel0):
    requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
    messages0 = requests.get(config.url + 'channel/messages/v2', params={"token": register1["token"], "channel_id": channel0["channel_id"], "start": 0})
    assert messages0.status_code == 403

def test_channel_messages_some_messages(clear, register0, channel0):
	# test channel messages with some messages, under 50
    send = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
    assert send.status_code == 200
    messages0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 0})
    assert messages0.status_code == 200
    response1 = messages0.json()
    assert response1['start'] == 0
    assert response1['end'] == -1
    assert len(response1['messages']) == 1


def test_messages_51_messages(clear, register0, channel0):
	# test channel messages with 51 messages
    message = 1
    for _ in range(51):
        requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
        message = message + 1
    response0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 0})
    response1 = response0.json()
    assert response0.status_code == 200
    assert response1['start'] == 0
    assert response1['end'] == 50
    assert len(response1['messages']) == 50


def test_messages_50_messages(clear, register0, channel0):
	# test channel messages with 50 messages 
	message = 0
	for _ in range(50):
		requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
		message = message + 1
	response0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 0})
	response1 = response0.json()
	assert len(response1["messages"]) == 50
	assert response1["start"] == 0
	assert response1["end"] == -1

def test_clear_messages(clear, register0, channel0):
	# clear message 
    send = requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
    message = send.json()
    requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 0})
    requests.delete(config.url + 'message/remove/v1', json={"token": register0["token"], "message_id": message["message_id"]})
    response3 = requests.get(config.url + 'channel/messages/v2', params={"token": register0['token'], "channel_id": channel0['channel_id'], "start": 0})
    response4 = response3.json()
    assert response3.status_code == 200
    assert len(response4["messages"]) == 0

def test_channel_messages_start_invalid(clear, register0, channel0):
    requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
    messages0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"], "start": 5})
    assert messages0.status_code == 400

def test_channel_messages_channel_id_invalid(clear, register0, channel0):
    requests.post(config.url + 'message/send/v1', json={"token": register0["token"], "channel_id": channel0["channel_id"], "message": "Hiiiiiii"})
    messages0 = requests.get(config.url + 'channel/messages/v2', params={"token": register0["token"], "channel_id": channel0["channel_id"] + 1, "start": 5})
    assert messages0.status_code == 400