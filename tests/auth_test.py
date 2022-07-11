''' 
Test cases for auth.py which contains functions auth_register_v1 and auth_login_v1
'''

import pytest
import hashlib
import jwt

from src.auth import auth_register_v1
from src.auth import auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.channel import channel_join_v2
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src.data_store import data_store

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

''' Tests for http layer '''

''' Tests for auth_register_v2 '''

''' Tests that an error is raised when the email provided is not in the correct format '''
def test_register_invalid_email2(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "invalidemail.com", "password": "password", "name_first": "Bob", "name_last": "Jones"})
	assert response1.status_code == 400

''' Tests that an error is raised when a user attempts to register with an email that has already been registered '''
def test_register_duplicate_email_invalid2(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Hunt"})
	assert response1.status_code == 200
	assert response2.status_code == 400

''' Tests that an error is raised when the password is less than 6 characters '''
def test_register_invalid_password2(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "abd", "name_first": "James", "name_last": "Hunt"})
	assert response1.status_code == 400

''' Tests that an error is raised when the first name is less than 1 or greater than 50 characters '''
def test_register_invalid_name_first(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "", "name_last": "Hunt"})
	assert response1.status_code == 400
	response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "name_last": "Hunt"})
	assert response2.status_code == 400

''' Tests that an error is raised when the last name is less than 1 or greater than 50 characters '''
def test_register_invalid_name_last(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": ""})
	assert response1.status_code == 400
	response2 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "James", "name_last": "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"})
	assert response2.status_code == 400

''' Tests that handle string is generated correctly '''
def test_register_handle_string(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail@gmail.com", "password": "1234abcd", "name_first": "J!amessssssss", "name_last": "H@untttttttt"})
	register1 = response1.json()
	response2 = requests.post(config.url + 'channels/create/v2', json={"token": register1['token'], "name": "test", "is_public": True})
	channel1 = response2.json()
	response3 = requests.get(config.url + 'channel/details/v2', params={"token": register1['token'], "channel_id": channel1['channel_id']})
	details1 = response3.json()
	response4 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234abcd", "name_first": "J!amessssssss", "name_last": "H@untttttttt"})
	register2 = response4.json()
	response5 = requests.post(config.url + 'channels/create/v2', json={"token": register2['token'], "name": "test", "is_public": True})
	channel2 = response5.json()
	response6 = requests.get(config.url + 'channel/details/v2', params={"token": register2['token'], "channel_id": channel2['channel_id']})
	details2 = response6.json()
	response7 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail3@gmail.com", "password": "1234abcd", "name_first": "J!amessssssss", "name_last": "H@untttttttt"})
	register3 = response7.json()
	response8 = requests.post(config.url + 'channels/create/v2', json={"token": register3['token'], "name": "test", "is_public": True})
	channel3 = response8.json()
	response9 = requests.get(config.url + 'channel/details/v2', params={"token": register3['token'], "channel_id": channel3['channel_id']})
	details3 = response9.json()
	assert details1['owner_members'][0]['handle_str'] != details2['owner_members'][0]['handle_str'] != details3['owner_members'][0]['handle_str']

''' Tests for auth_login_v2 '''

''' Tests that an error is raised when a user attempts to login with an email that doesn't match for a registered user '''
def test_login_email_exists(clear, register1):
	response1 = requests.post(config.url + 'auth/login/v2', json={"email": "nonexistentemail@gmail.com", "password": "1234abcd"})
	assert response1.status_code == 400

''' Tests that an error is raised when a user logs in with the wrong password '''
def test_login_password_matches(clear, register1):
	response1 = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234efgh"})
	assert response1.status_code == 400

''' Tests that the user_id given by auth_login matches that of auth_register '''
def test_login_valid(clear, register1):
	response1 = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234abcd"})
	assert response1.status_code == 200

''' Tests for auth_logout_v1 '''

''' Tests that a user is logged out '''
def test_logout_valid(clear, register1):
	response1 = requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
	output = response1.json()
	assert response1.status_code == 200
	assert output == {}

''' Tests that an error is raised when an invalid token is given '''
def test_logout_invalid(clear, register1):
	requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
	response2 = requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
	assert response2.status_code == 403

''' Tests that a user can logout multiple times if they have multiple sessions '''
def test_logout_multiple_times(clear, register1):
	login1_response = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234abcd"})
	login1 = login1_response.json()
	login2_response = requests.post(config.url + 'auth/login/v2', json={"email": "validemail@gmail.com", "password": "1234abcd"})
	login2 = login2_response.json()
	logout1 = requests.post(config.url + 'auth/logout/v1', json={"token": register1['token']})
	logout2 = requests.post(config.url + 'auth/logout/v1', json={"token": login1['token']})
	logout3 = requests.post(config.url + 'auth/logout/v1', json={"token": login2['token']})
	assert logout1.status_code == 200
	assert logout2.status_code == 200
	assert logout3.status_code == 200

''' Tests that a user can logout when there are multiple users '''
def test_logout_multiple_users(clear, register1):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "validemail2@gmail.com", "password": "1234efgh", "name_first": "Aaleen", "name_last": "Ahmed"})
	register2 = response1.json()
	logout1 = requests.post(config.url + 'auth/logout/v1', json={"token": register2['token']})
	assert logout1.status_code == 200


''' Tests for passwordreset_request'''

''' Test for valid password reset request'''
def test_auth_passwordreset_request(clear):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "ashnadesai17@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
	register2 = response1.json()
	# change to blackbox
	requests.post(config.url + 'auth/logout/v1', json={"token": register2['token']})
	response2 = requests.post(config.url + 'auth/passwordreset/request/v1', json={"email": "ashnadesai17@gmail.com"})
	assert response2.status_code == 200

''' Tests for valid password reset'''
def test_auth_passwordreset(clear, register1):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "ashnadesai17@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
	register1 = response1.json()
	requests.post(config.url + 'auth/passwordreset/request/v1', json={"email": 'ashnadesai17@gmail.com'})
	store = data_store.get()
	for codes in store['reset_codes']:
		if register1['email'] == codes['email']:
			reset = requests.post(config.url + 'auth/passwordreset/reset/v1', json={"reset_code": codes['reset_code'], "new_password": "Abc123"})
			reset_response = reset.json()
			assert reset_response == 200
	for user in store['users']:
		if user['u_id'] == register1['u_id']:
			assert user['password'] == hashlib.sha256("Abc123".encode()).hexdigest()

''' Tests for invalid password'''
def test_auth_passwordreset_invalidpassword(clear, register1):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "ashnadesai17@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
	register1 = response1.json()
	requests.post(config.url + 'auth/passwordreset/request/v1', json={"email": 'ashnadesai17@gmail.com'})
	store = data_store.get()
	for codes in store['reset_codes']:
		if register1['email'] == codes['email']:
			reset = requests.post(config.url + 'auth/passwordreset/reset/v1', json={"reset_code": codes['reset_code'], "new_password": "abc"})
			reset_response = reset.json()
			assert reset_response == 400

''' Tests for invalid code'''
def test_auth_passwordreset_invalidcode(clear, register1):
	response1 = requests.post(config.url + 'auth/register/v2', json={"email": "ashnadesai17@gmail.com", "password": "1234efgh", "name_first": "Ashna", "name_last": "Desai"})
	register1 = response1.json()
	requests.post(config.url + 'auth/passwordreset/request/v1', json={"email": 'ashnadesai17@gmail.com'})
	store = data_store.get()
	for codes in store['reset_codes']:
		if register1['email'] == codes['email']:
			reset = requests.post(config.url + 'auth/passwordreset/reset/v1', json={"reset_code": codes['reset_code'] + 3, "new_password": "abc1234"})
			reset_response = reset.json()
			assert reset_response == 400

