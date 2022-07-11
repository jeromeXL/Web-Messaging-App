''' 
Test cases for dm.py which contains functions dm_create, dm_list, dm_remove, dm_details, dm_leave and dm_messages
'''

import pytest
from src.auth import *
from src.dm import *
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

''' Tests for dm_create '''

''' Tests that an error is raised when the token is invalid '''
def test_dm_create_invalid_token(clear_and_register1, register2):
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    assert response2.status_code == 403

''' Tests that an error is raised when a u_id given in the list u_ids is not valid '''
def test_dm_create_u_id_invalid(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id'] + clear_and_register1['auth_user_id']]})
    assert response2.status_code == 400

''' Tests that an error is raised when a duplicate u_id is given in the list u_ids '''
def test_dm_create_duplicate_u_id(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id'], register2['auth_user_id']]})
    assert response2.status_code == 400

''' Tests that dm_create gives a dictionary containing the dm_id which is an integer '''
def test_dm_create_valid_output(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    assert response2.status_code == 200
    assert isinstance(dm_created['dm_id'], int) == True

''' Tests that dm_create stores a new unique dm '''
def test_dm_create_dm_stored(clear_and_register1, register2):
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234ijkl", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id'], register3['auth_user_id']]})
    dm_created1 = response3.json()
    response4 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    dm_list1 = response4.json()
    response5 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    dm_created2 = response5.json()
    response6 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    dm_list2 = response6.json()
    assert response6.status_code == 200
    assert dm_created1['dm_id'] != dm_created2['dm_id']
    assert dm_list1['dms'] != dm_list2['dms']
    assert (len(dm_list1['dms'])) == 1 and (len(dm_list2['dms']) == 2)

''' Tests for dm_messages '''

''' Tests that an error is raised when the token is invalid '''
def test_dm_messages_invalid_token(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response3 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1['token'], "dm_id": dm_created['dm_id'], "start": 0})
    assert response3.status_code == 403

''' Tests that an error is raised when user is not a member of the dm '''
def test_dm_messages_user_not_in_dm(clear_and_register1, register2):
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234ijkl", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response3.json()
    response4 = requests.get(config.url + 'dm/messages/v1', params={"token": register3['token'], "dm_id": dm_created['dm_id'], "start": 0})
    assert response4.status_code == 403

''' Tests that an error is raised when dm_id does not refer to a valid dm '''
def test_dm_messages_dm_invalid(clear_and_register1, register2):
    response2 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1['token'], "dm_id": register2['auth_user_id'], "start": 0})
    assert response2.status_code == 400

''' Tests that an error is raised when start is greater than the total number of messages in the channel '''
def test_dm_messages_start_greater(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    response3 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1['token'], "dm_id": dm_created['dm_id'], "start": 5})
    assert response3.status_code == 400

''' Tests valid output is given when no messages have been sent '''
def test_dm_messages_valid(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    response3 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1['token'], "dm_id": dm_created['dm_id'], "start": 0})
    messages = response3.json()
    assert response3.status_code == 200
    assert messages == { 'messages': [], 'start': 0, 'end': -1}


'''Tests valid output is given when less than 50 messages have been sent '''
def test_dm_messages_less_than_10(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    for _ in range(10):
        requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_created["dm_id"], "message": "hi"})
    response0 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1["token"], "dm_id": dm_created["dm_id"], "start": 0})
    messages = response0.json()
    assert len(messages["messages"]) == 10
    assert messages["start"] == 0
    assert messages["end"] == -1

''' Tests valid output is given when more than 50 messages have been sent '''
def test_dm_messages_more_than_50(clear_and_register1, register2):
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_created = response2.json()
    for _ in range(51):
        requests.post(config.url + 'message/senddm/v1', json={"token": clear_and_register1["token"], "dm_id": dm_created["dm_id"], "message": "Hiiiiiii"})
    response0 = requests.get(config.url + 'dm/messages/v1', params={"token": clear_and_register1["token"], "dm_id": dm_created["dm_id"], "start": 0})
    messages = response0.json()
    assert response0.status_code == 200
    assert messages['start'] == 0
    assert messages['end'] == 50
    assert len(messages['messages']) == 50


''' Tests for dm_list'''

''' Tests invalid token '''
def test_dm_list_invalid_token(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response3 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    assert response3.status_code == 403

''' Test for one dm between two users'''
def test_dm_list_valid(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    response3 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    list = response3.json()
    assert response3.status_code == 200
    assert list == {'dms': [{'dm_id': 1,
    'name': 'aaleenahmed, jameshunt'}]}

''' Test for multiple dms, list only prints dms with user '''
def test_multiple_dm_list_valid(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    requests.post(config.url + 'dm/create/v1', json={"token": register3['token'], "u_ids": [register2['auth_user_id']]})
    response4 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    list = response4.json()
    assert response4.status_code == 200
    assert list == {'dms': [{'dm_id': 1,
    'name': 'aaleenahmed, jameshunt'}, 
    {'dm_id': 2,
    'name': 'ashnadesai, jameshunt'}]
    }


''' Tests for dm_remove '''
''' Tests invalid token '''
def test_dm_remove_invalid_token(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response3 = requests.delete(config.url + 'dm/remove/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 403

''' Valid test that deletes one dm from list'''
def test_dm_delete_dm(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    dm_id_returned = response3.json()
    response5 = requests.delete(config.url + 'dm/remove/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response5.status_code == 200
    response4 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    assert response4.json() == {'dms': [{'dm_id': 1,
    'name': 'aaleenahmed, jameshunt'}]}
    
''' Invalid input if member is not a member of dm'''
def test_dm_remove_member_false(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": register3['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response3.json()
    response5 = requests.delete(config.url + 'dm/remove/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response5.status_code == 403

''' Test for input error if dm_id is not valid'''
''' Delete this line please... '''
def test_dm_delete_input_error(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    response5 = requests.delete(config.url + 'dm/remove/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id'] + 3})
    assert response5.status_code == 400
    response4 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    assert response4.json() == response3.json()

''' Test for access error if dm_id is valid but user is not creator'''
def test_dm_delete_access_error1(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    response5 = requests.delete(config.url + 'dm/remove/v1', json={"token": register2['token'], "dm_id": dm_id_returned['dm_id']})
    assert response5.status_code == 403
    response4 = requests.get(config.url + 'dm/list/v1', params={"token": clear_and_register1['token']})
    assert response4.json() == response3.json()

''' Test for access error if user is creator of dm but has left'''
def test_dm_delete_access_error2(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    requests.post(config.url + 'dm/leave/v1', json={"token": clear_and_register1['token'], "dm_id": [dm_id_returned['dm_id']]})
    response3 = requests.delete(config.url + 'dm/remove/v1', json={"token": register2['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 403

''' Tests for dm_details'''
''' Tests invalid token '''
def test_dm_details_invalid_token(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response3 = requests.get(config.url + 'dm/details/v1', params={"token": clear_and_register1['token'], "dm_id": [dm_id_returned['dm_id']]})
    assert response3.status_code == 403

''' Test details are returned correctly for 1 dm'''
def test_dm_details_one_dm(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.get(config.url + 'dm/details/v1', params={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 200
    assert response3.json() == {
        'name': 'aaleenahmed, jameshunt',
        'members': [
            {
                'email': 'validemail@gmail.com',
                'handle_str': 'jameshunt',
                'name_first': 'James',
                'name_last': 'Hunt',
                'u_id': 1
            },
            {
                'email': 'validemail2@gmail.com',
                'handle_str': 'aaleenahmed',
                'name_first': 'Aaleen',
                'name_last': 'Ahmed',
                'u_id': 2
            }]
    }
''' Test detaisl are returned when multiple dms exist'''
def test_dm_details_mult_dm(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response3.json()
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    response5 = requests.get(config.url + 'dm/details/v1', params={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response5.status_code == 200
    assert response5.json() == {
        'name': 'aaleenahmed, jameshunt',
        'members': [
            {
                'email': 'validemail@gmail.com',
                'handle_str': 'jameshunt',
                'name_first': 'James',
                'name_last': 'Hunt',
                'u_id': 1
            },
            {
                'email': 'validemail2@gmail.com',
                'handle_str': 'aaleenahmed',
                'name_first': 'Aaleen',
                'name_last': 'Ahmed',
                'u_id': 2
            }]
    }


''' Test input error if dm does not exist'''
def test_dm_details_input_error(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.get(config.url + 'dm/details/v1', params={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id'] + 3})
    assert response3.status_code == 400

''' Test input error if user is not a member of the dm'''
def test_dm_details_access_error(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.get(config.url + 'dm/details/v1', params={"token": register3['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 403


'''Tests for dm_leave'''
''' Tests invalid token '''
def test_dm_leave_invalid_token(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    requests.post(config.url + 'auth/logout/v1', json={"token": clear_and_register1['token']})
    response3 = requests.post(config.url + 'dm/leave/v1', json={"token": clear_and_register1['token'], "dm_id": [dm_id_returned['dm_id']]})
    assert response3.status_code == 403

''' Test valid output of user leaving a dm'''
def test_dm_leave_valid(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.post(config.url + 'dm/leave/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 200
    response4 = requests.get(config.url + 'dm/details/v1', params={"token": register2['token'], "dm_id": dm_id_returned['dm_id']})
    dm_details = response4.json()
    assert dm_details == {
        'name': 'aaleenahmed, jameshunt',
        'members': [
            {
                'email': 'validemail2@gmail.com',
                'handle_str': 'aaleenahmed',
                'name_first': 'Aaleen',
                'name_last': 'Ahmed',
                'u_id': 2
            }]
    }

''' Valid test for multiple dms'''
def test_dm_leave_multiple_dms(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id'], register3['auth_user_id']]})
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register3['auth_user_id']]})
    requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response3.json()
    response5 = requests.post(config.url + 'dm/leave/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id']})
    assert response5.status_code == 200
    response4 = requests.get(config.url + 'dm/details/v1', params={"token": register2['token'], "dm_id": dm_id_returned['dm_id']})
    dm_details = response4.json()
    assert dm_details == {
        'name': 'aaleenahmed, ashnadesai, jameshunt',
        'members': [
            {
                'email': 'validemail2@gmail.com',
                'handle_str': 'aaleenahmed',
                'name_first': 'Aaleen',
                'name_last': 'Ahmed',
                'u_id': 2
            }, 
            {
                'email': 'validemail3@gmail.com',
                'handle_str': 'ashnadesai',
                'name_first': 'Ashna',
                'name_last': 'Desai',
                'u_id': 3
            }, 
            ]
    }

'''Test for input error where dm_id is incorrect'''
def test_dm_leave_input_error(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response2.json()
    response3 = requests.post(config.url + 'dm/leave/v1', json={"token": clear_and_register1['token'], "dm_id": dm_id_returned['dm_id'] + 3})
    assert response3.status_code == 400

'''Test for access error where member is not member of dm'''
def test_dm_leave_access_error(clear_and_register1):
    response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
    register2 = response1.json()
    response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
    register3 = response2.json()
    response3 = requests.post(config.url + 'dm/create/v1', json={"token": clear_and_register1['token'], "u_ids": [register2['auth_user_id']]})
    dm_id_returned = response3.json()
    response3 = requests.post(config.url + 'dm/leave/v1', json={"token": register3['token'], "dm_id": dm_id_returned['dm_id']})
    assert response3.status_code == 403
