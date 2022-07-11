''' 
Test cases for channels.py which contains functions
1) channels_list_v1 
2) channels_listall_v1
3) channels_create_v1
'''

import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_listall_v1
from src.channels import channels_list_v1 
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src import config
import requests
import json

''' Fixture that clears data_store and registers a valid user '''
@pytest.fixture
def clear_and_register1():
    requests.delete(config.url + 'clear/v1')
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register1 = response.json()
    return register1

@pytest.fixture 
def creates_channel(clear_and_register1):
    response = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "Jerome", "is_public": True})
    channel1 = response.json()
    return channel1
'''
#create / testing id is an integer 
def test_create_valid():
    clear_v1()
    user_id = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
    temp_channel = channels_create_v1(user_id['auth_user_id'], "JeromeChiu", True)
    assert isinstance(temp_channel['channel_id'], int) == True

#create / testing ids are unique
def test_unique_id():
    clear_v1()
    user_id = auth_register_v1("validemailasdf@gmail.com", "1234abcd2", "James2", "Hunt2")
    user_id2 = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
    id1 = channels_create_v1(user_id['auth_user_id'],"AaleenAhmed", True)
    id2 = channels_create_v1(user_id2['auth_user_id'],"OliverXu", True)
    assert id1['channel_id'] != id2['channel_id']

#create / tesing length of name is at least 1

def test_create_length_name1():
    clear_v1()
    with pytest.raises(InputError):
        user_id = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
        channels_create_v1(user_id['auth_user_id'], "", True)
    

#create / testing length of name is not more than 20

def test_create_length_name20():
    clear_v1()
    with pytest.raises(InputError):
        user_id = auth_register_v1("validemail@gmail.com", "1234abcd", "James", "Hunt")
        channels_create_v1(user_id['auth_user_id'], "abcdefghijklmnopqrstuvwxyz", True)
        

#listall / input User1 auth_user_id, output both User1 and User2
def test_listall1():
    clear_v1()
    user1 = auth_register_v1('jeromechiu@gmail.com', 'ThisISPassword43', 'Jerome', 'Chiu')
    user2 = auth_register_v1('karlchiu@gmail.com', 'ThisISPassword56', 'Karl', 'Chiu') 
    channel1 = channels_create_v1(user1['auth_user_id'], "JeromeChiu", True)
    channel2 = channels_create_v1(user2['auth_user_id'], "KarlChiu", True)
    listall1 = channels_listall_v1(user1['auth_user_id'])
    assert listall1 == {'channels': [{'channel_id': channel1['channel_id'], 'name': 'JeromeChiu'}, {'channel_id': channel2['channel_id'], 'name': 'KarlChiu'}]}
    
#listall / input User2 auth_user_id, output both User1 and User2
def test_listall2(): 
    clear_v1()
    user1 = auth_register_v1('jeromechiu@gmail.com', 'ThisISPassword43', 'Jerome', 'Chiu')
    user2 = auth_register_v1('karlchiu@gmail.com', 'ThisISPassword56', 'Karl', 'Chiu') 
    channel1 = channels_create_v1(user1['auth_user_id'], "JeromeChiu", True)
    channel2 = channels_create_v1(user2['auth_user_id'], "KarlChiu", True)
    listall2 = channels_listall_v1(user2['auth_user_id'])
    assert listall2 == {'channels': [{'channel_id': channel1['channel_id'], 'name': 'JeromeChiu'}, {'channel_id': channel2['channel_id'], 'name': 'KarlChiu'}]}
    

    
#list / input User1 auth_user_id, returning only User1
def test_list1():
    clear_v1()
    user1 = auth_register_v1('jeromechiu@gmail.com', 'ThisISPassword43', 'Jerome', 'Chiu')
    #user2 = auth_register_v1('karlchiu@gmail.com', 'ThisISPassword56', 'Karl', 'Chiu') 
    channel1 = channels_create_v1(user1['auth_user_id'], "JeromeChiu", True)
    #channel2 = channels_create_v1(user2['auth_user_id'], "KarlChiu", True)
    list1 = channels_list_v1(user1['auth_user_id'])
    assert list1 == {'channels': [{'channel_id': channel1['channel_id'], 'name': 'JeromeChiu'}]}
    
#list / input User2 auth_user_id, returning only User2
def test_list2():
    clear_v1()
    #user1 = auth_register_v1('jeromechiu@gmail.com', 'ThisISPassword43', 'Jerome', 'Chiu')
    user2 = auth_register_v1('karlchiu@gmail.com', 'ThisISPassword56', 'Karl', 'Chiu') 
    #channel1 = channels_create_v1(user1['auth_user_id'], "JeromeChiu", True)
    channel2 = channels_create_v1(user2['auth_user_id'], "KarlChiu", True)
    list2 = channels_list_v1(user2['auth_user_id'])
    assert list2 == {'channels': [{'channel_id': channel2['channel_id'], 'name': 'KarlChiu'}]}
'''
#list / create user 1, create channel 1, create channel 2, 

def test_list(clear_and_register1, creates_channel):
    
    response2 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "Jerome", "is_public": True})
    channel2 = response2.json()
    response = requests.get(config.url + 'channels/list/v2', params={"token": clear_and_register1['token']})
    list1 = response.json()
    assert list1['channels'][0]['channel_id'] == creates_channel['channel_id']
    assert list1['channels'][1]['channel_id'] == channel2['channel_id']

''' Tests that an error is raised when the token is invalid '''
def test_list_token_invalid(clear_and_register1, creates_channel):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.get(config.url + 'channels/list/v2', params={"token": clear_and_register1["token"]})
    assert response1.status_code == 403
    
    
#listall / create user 1& 2, create seperate channels with user 1&2, return channels 1&2

def test_listall(clear_and_register1, creates_channel):
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
    register2 = response.json()
    
    response2 = requests.post(config.url + 'channels/create/v2', json={"token": register2["token"], "name": "Jerome", "is_public": True})
    channel2 = response2.json()
    
    response = requests.get(config.url + 'channels/listall/v2', params={"token": clear_and_register1['token']})
    list1 = response.json()
    assert list1['channels'][0]['channel_id'] == creates_channel['channel_id']
    assert list1['channels'][1]['channel_id'] == channel2['channel_id']
    
''' Tests that an error is raised when the token is invalid '''
def test_list_all_token_invalid(clear_and_register1, creates_channel):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.get(config.url + 'channels/listall/v2', params={"token": clear_and_register1["token"]})
    assert response1.status_code == 403


''' Tests that an error is raised when the token is invalid '''
def test_create_token_invalid(clear_and_register1):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1["token"]})
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "Jerome", "is_public": True})
    assert response1.status_code == 403


''' Name < 0 or Name>20 '''
def test_create_name_invalid(clear_and_register1):
    response1 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "", "is_public": True})
    response2 = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "JeromeJeromeJeromeJerome", "is_public": True})
    assert response1.status_code == 400
    assert response2.status_code == 400
    
''' Tests output is valid when given correct inputs '''
def test_create_valid(clear_and_register1, creates_channel):
    response = requests.get(config.url + 'channels/list/v2', params={"token": clear_and_register1['token']})
    list1 = response.json()
    assert list1['channels'][0]['channel_id'] == creates_channel['channel_id']