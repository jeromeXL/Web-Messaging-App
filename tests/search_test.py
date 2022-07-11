''' 
Test cases for search.py which contains the function search
'''

import pytest
from src.auth import *
from src.error import *
from src.other import *
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

''' Fixture that registers a second valid user '''
@pytest.fixture
def register2():
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response.json()
    return register2

''' Fixture that registers a third valid user '''
@pytest.fixture
def register3():
    response = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234ijkl", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response.json()
    return register3

''' Fixture that creates a channel '''
@pytest.fixture
def channel_create(clear_and_register1):
	response = requests.post(config.url + 'channels/create/v2', json={"token": clear_and_register1["token"], "name": "test", "is_public": True})
	channel_create = response.json()
	return channel_create

''' Fixture that creates a dm '''
@pytest.fixture
def dm_create(clear_and_register1, register2):
	response = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1["token"], "u_ids": [register2["auth_user_id"]]})
	dm_create = response.json()
	return dm_create

@pytest.fixture
def message_channel(clear_and_register1, channel_create):
    requests.post(config.url + 'message/send/v1', json={"token": clear_and_register1["token"], "channel_id": channel_create["channel_id"], "message": "how are you doing"})
    requests.post(config.url + 'message/send/v1', json={"token": clear_and_register1["token"], "channel_id": channel_create["channel_id"], "message": "hello friend"})
    requests.post(config.url + 'message/send/v1', json={"token": clear_and_register1["token"], "channel_id": channel_create["channel_id"], "message": "good to see you"})
    requests.post(config.url + 'message/send/v1', json={"token": clear_and_register1["token"], "channel_id": channel_create["channel_id"], "message": "alright hello"})
    requests.post(config.url + 'message/send/v1', json={"token": clear_and_register1["token"], "channel_id": channel_create["channel_id"], "message": "hi"})

@pytest.fixture
def message_dm(clear_and_register1, dm_create):
    requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_create["dm_id"], "message": "hello"})
    requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_create["dm_id"], "message": "HeLLo"})
    requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_create["dm_id"], "message": "how are you"})
    requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_create["dm_id"], "message": "friend"})
    requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_create["dm_id"], "message": "hellO"})

''' Tests for function search '''

''' Tests that an error is raised when the token is invalid '''
def test_search_token_invalid(clear_and_register1, channel_create):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response2 = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": 'hello'})
    assert response2.status_code == 403

''' Tests that an error is raised when the query_str length is too long '''
def test_search_query_str_long(clear_and_register1, channel_create):
    query_str = 'hello'
    query_str = query_str * 300
    response = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": query_str})
    assert response.status_code == 400

''' Tests that an error is raised when the query_str length is too short '''
def test_search_query_str_short(clear_and_register1, channel_create):
    response = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": ''})
    assert response.status_code == 400

''' Tests that correct messages are returned from channels '''
def test_search_valid_channels(clear_and_register1, register2, message_channel):
    requests.post(config.url + 'channels/create/v2', json={"token": register2["token"], "name": "test2", "is_public": True})
    response = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": 'hello'})
    messages = response.json()
    assert response.status_code == 200
    assert len(messages['messages']) == 2

''' Tests that correct messages are returned from dms '''
def test_search_valid_dms(clear_and_register1, message_dm, register2, register3):
    requests.post(config.url + 'dm/create/v1', json={"token": register3["token"], "u_ids": [register2["auth_user_id"]]})
    response = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": 'hello'})
    messages = response.json()
    assert response.status_code == 200
    assert len(messages['messages']) == 3

''' Tests that correct messages are returned from channels and dms '''
def test_search_valid(clear_and_register1, message_channel, message_dm):
    response = requests.get(config.url + 'search/v1', params={"token": clear_and_register1['token'], "query_str": 'hello'})
    messages = response.json()
    assert response.status_code == 200
    assert len(messages['messages']) == 5