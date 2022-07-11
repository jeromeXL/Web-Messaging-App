''' 
Test cases for admin.py which contains functions admin_user_remove and admin_userpermission_change
'''

import pytest
from pylint import *
from src.auth import *
from src.admin import *
from src.error import *
import requests
import json
from src import config
from src.channel import *
from src.other import *
from src.channels import *
from src.data_store import *
from src import *
from src.dm import *
from src.message import*

''' Fixture that clears data_store and registers a valid user '''
@pytest.fixture
def clear_and_register1():
    requests.delete(config.url + 'clear/v1')
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register1 = response.json()
    return register1

''' Fixture that registers a second valid user '''
@pytest.fixture
def register2():
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response.json()
    return register2


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
def dm_1(new_user_1, new_user_2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": new_user_1['token'], "u_ids":[new_user_2['auth_user_id']]})
    dm = response2.json()
    return dm

@pytest.fixture
def dm_2(new_user_1, new_user_2, new_user_3):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": new_user_1['token'], "u_ids": [new_user_2['auth_user_id'], new_user_3['auth_user_id']]})
    dm2 = response2.json()
    return dm2

#tests for admin/user/remove/v1

#tests to see if user is removed successfully 
def test_admin_user_remove_successful(clear, new_user_1, new_user_2, new_user_3, channel_public, channel_public2, dm_1, dm_2):
    """ admin user remove if successful"""

    #checks if user 2 is in the channels and dms
    requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "u_id" : new_user_2['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public2['channel_id'], "u_id" : new_user_2['auth_user_id']})
    requests.post(config.url + 'channel/invite/v2', json={"token" : new_user_1['token'], "channel_id" : channel_public2['channel_id'], "u_id" : new_user_3['auth_user_id']})
    response1 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']})
    assert response1.status_code == 200
    response2 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2['token'], "channel_id" : channel_public['channel_id']})
    assert response2.status_code == 200
    response3 = requests.get(config.url + 'dm/details/v1', params={"token" : new_user_2['token'], "dm_id" : dm_1['dm_id']})
    assert response3.status_code == 200
    response4 = requests.get(config.url + 'dm/details/v1', params={"token" : new_user_2['token'], "dm_id" : dm_2['dm_id']})
    assert response4.status_code ==200
   
    #send messages in dms and channels
    requests.post(config.url + 'message/send/v1', json = {"token" : new_user_2['token'], "channel_id" : channel_public["channel_id"], "message" : "hello"})
    requests.post(config.url + 'message/send/v1', json = {"token" : new_user_2['token'], "channel_id" : channel_public["channel_id"], "message" : "hi"})
    
    requests.post(config.url + 'message/send/v1', json = {"token" : new_user_2['token'], "channel_id" : channel_public2["channel_id"], "message" : "hello"})
    a = requests.post(config.url + 'message/send/v1', json = {"token" : new_user_3['token'], "channel_id" : channel_public2["channel_id"], "message" : "hi"})
    assert a.status_code == 200
    requests.post(config.url + 'message/senddm/v1', json = {"token" : new_user_2['token'], "dm_id" : dm_1['dm_id'], "message" : "hello"})
    requests.post(config.url + 'message/senddm/v1', json = {"token" : new_user_2['token'], "dm_id" : dm_1['dm_id'], "message" : "hi"})
    
    requests.post(config.url + 'message/senddm/v1', json = {"token" : new_user_2['token'], "dm_id" : dm_2['dm_id'], "message" : "hello"})
    requests.post(config.url + 'message/senddm/v1', json = {"token" : new_user_3['token'], "dm_id" : dm_2['dm_id'], "message" : "hi"})


    #remove user
    response5 = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response5.status_code == 200
    
    #check to see if user token is invalidated
    response6 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_2['token'], "channel_id" : channel_public["channel_id"]})
    assert response6.status_code == 403

    #check first channel
    response7 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id']})
    assert response7.status_code == 200
    details = response7.json() 
    assert (len(details['all_members']) == 1)
    response71 = requests.get(config.url + 'channel/messages/v2', params={"token" : new_user_1['token'], "channel_id" : channel_public['channel_id'], "start" : 0})
    messages1 = response71.json()
    assert(messages1['messages'][0].get('message') == "Removed user")
    assert(messages1['messages'][1].get('message') == "Removed user")

    #check second channel -- check
    response8 = requests.get(config.url + 'channel/details/v2', params={"token" : new_user_1['token'], "channel_id" : channel_public2['channel_id']})
    assert response8.status_code == 200
    details2 = response8.json() 
    assert (len(details2['all_members']) == 2)
    response81 = requests.get(config.url + 'channel/messages/v2', params={"token" : new_user_1['token'], "channel_id" : channel_public2['channel_id'], "start" : 0})
    messages81 = response81.json()
    assert(messages81['messages'][1].get('message') =="Removed user")
    assert(messages81['messages'][0].get('message') == 'hi')


    #check first dm
    response9 = requests.get(config.url + 'dm/details/v1', params={"token" : new_user_1['token'], "dm_id" : dm_1['dm_id']})
    dm_details1 = response9.json()
    assert (len(dm_details1['members']) == 1)
    response91 = requests.get(config.url + 'dm/messages/v1', params={"token" : new_user_1['token'], "dm_id" : dm_1['dm_id'], "start" : 0})
    messages91 = response91.json()
    assert(messages91['messages'][0].get('message') == "Removed user")
    assert(messages91['messages'][1].get('message') == "Removed user")
    
    #check second dm
    response10 = requests.get(config.url + 'dm/details/v1', params={"token" : new_user_1['token'], "dm_id" : dm_2['dm_id']})
    dm_details2 = response10.json()
    assert (len(dm_details2['members']) == 2)
    response101 = requests.get(config.url + 'dm/messages/v1', params={"token" : new_user_1['token'], "dm_id" : dm_2['dm_id'], "start" : 0})
    messages101 = response101.json()
    assert(messages101['messages'][1].get('message') == "Removed user")
    assert(messages101['messages'][0].get('message') == "hi")

    #check user profile
    response11 = requests.get(config.url + 'user/profile/v1', params={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    userprofile = response11.json()
    assert userprofile['user']['email'] == ''
    assert userprofile['user']['name_first'] == 'Removed'
    assert userprofile['user']['name_last'] == 'user'
    assert userprofile['user']['handle_str'] == ''


def test_admin_user_remove_not_global_owner(clear, new_user_1, new_user_2, new_user_3):
    """ admin user removal non global owner"""
    response1 = requests.post(config.url+ 'auth/register/v2', json={"email" : "c1@c.com", "password": "cbbbbbbb", "name_first" : "c", "name_last": "c"})
    user3 =response1.json()
    requests.post(config.url + "admin/userpermission/change/v1", json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id'], "permission_id" : 1})
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_3['token'], "u_id" : user3['auth_user_id'] })
    assert response.status_code == 403
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : user3['token'], "u_id" : new_user_3['auth_user_id'] })

    response2 = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_2['token'], "u_id" : user3['auth_user_id'] })
    assert response2.status_code == 200

def test_admin_user_remove_invalid_u_id(clear, new_user_1, new_user_2):
    """ admin remove u_id that is invalid"""
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']+3 })
    assert response.status_code == 400

def test_admin_user_remove_one_global_owner(clear, new_user_1, new_user_2):
     """ admin user remove a global owner """
     response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_1['auth_user_id'] })
     assert response.status_code == 400

def test_admin_user_invalid_token(clear, new_user_1, new_user_2):
    """ admin user with invalid token """
    requests.post(config.url + 'auth/logout/v1', json={"token": new_user_1['token']})
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 403

def test_admin_user_remove_owner_member_channel(clear, new_user_1, new_user_2):
    """ admin user remove owner"""
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": new_user_2['token'], "name" : "test", "is_public" : True })
    assert response1.status_code == 200
    print(response1)
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200    


def test_admin_user_remove_dm_owner(clear, new_user_1, new_user_2):
    """ admin remove dm_owner """
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": new_user_2['token'], "u_ids": [new_user_1['auth_user_id'], new_user_2['auth_user_id']]})
    assert response2.status_code == 200
    print (response2)
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code ==200

def test_admin_user_once_removed_user_cant_do_anything(clear, new_user_1, new_user_2):
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
    response2 = requests.post(config.url + 'channels/create/v2', json={"token": new_user_2['token'], "name" : "test", "is_public" : True })
    print (response2)
    assert response2.status_code == 403

def test_admin_user_reusable_email(clear, new_user_1, new_user_2):
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
    response2= requests.post(config.url+ 'auth/register/v2', json={"email" : "b@b.com", "password": "bbbbbbbb", "name_first" : "b", "name_last": "b"})
    assert response2.status_code == 200

def test_admin_user_remove_global_remove_globa(clear, new_user_1, new_user_2):
    requests.post(config.url + "admin/userpermission/change/v1", json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id'], "permission_id" : 1})
    response = requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_2['token'], "u_id" : new_user_2['auth_user_id']})
    assert response.status_code == 200
   
def test_admin_user_remove_users_all(clear, new_user_1, new_user_2):
    response1 = requests.get(config.url + "users/all/v1", params={'token' : new_user_1['token']})
    allusers1 = response1.json()
    assert allusers1['users'][1]['email'] == 'b@b.com'
    assert len(allusers1['users']) == 2
    requests.delete(config.url + 'admin/user/remove/v1', json={"token" : new_user_1['token'], "u_id" : new_user_2['auth_user_id']})
    response = requests.get(config.url + "users/all/v1", params={'token' : new_user_1['token']})
    allusers = response.json()
    assert len(allusers['users']) == 1
    

''' Tests for admin_userpermission_change '''

''' Tests that an error is raised when token is invalid '''
def test_permissionchange_token_invalid(clear_and_register1, register2):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": register2['auth_user_id'], "permission_id": 1})
    assert response.status_code == 403

''' Tests that an error is raised when the user is not a global owner '''
def test_permissionchange_not_global(clear_and_register1, register2):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": register2['token'], "u_id": clear_and_register1['auth_user_id'], "permission_id": 2})
    assert response.status_code == 403

''' Tests that an error is raised when the u_id is invalid '''
def test_permissionchange_u_id_invalid(clear_and_register1, register2):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": register2['auth_user_id'] + clear_and_register1['auth_user_id'], "permission_id": 1})
    assert response.status_code == 400

''' Tests that an error is raised when the only global owner tries to change permission_id '''
def test_permissionchange_only_global(clear_and_register1, register2):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": clear_and_register1['auth_user_id'], "permission_id": 2})
    assert response.status_code == 400

''' Tests that an error is raised when the permission id is invalid '''
def test_permissionchange_permission_invalid(clear_and_register1, register2):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": register2['auth_user_id'], "permission_id": 5})
    assert response.status_code == 400

''' Tests that an error is raised when the user already has that level of permission id '''
def test_permissionchange_already_permission(clear_and_register1):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": clear_and_register1['auth_user_id'], "permission_id": 1})
    assert response.status_code == 400

''' Tests that a user is able to change permission_id when inputs are valid as they are not global '''
def test_permissionchange_valid(clear_and_register1, register2):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234ijkl", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response.json()
    response1 = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": clear_and_register1['token'], "u_id": register2['auth_user_id'], "permission_id": 1})
    assert response1.status_code == 200
    response2 = requests.post(config.url + 'admin/userpermission/change/v1', json={"token": register2['token'], "u_id": register3['auth_user_id'], "permission_id": 1})
    assert response2.status_code == 200

