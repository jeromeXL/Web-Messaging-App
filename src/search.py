from src.data_store import data_store
from src.error import *
from src.auth import *

'''
SEARCH

Returns a collection of messages in channels/DM that the user has joined that contains a
given query string (case-insesitive)

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    query_str (string)      - the string which you want all messages returned to contain 

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    InputError  - Occurs when the length of query_str is less than 1 or over 1000 characters

Return Value:
    Returns a dictionary containing messages which is a list of dictionaries containing 
    information about a message
'''

def search(token, query_str):
    
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if len(query_str) > 1000 or len(query_str) < 1:
        raise InputError("Length of query string invalid")

    messages = []
    for channel in store['channels']:
        if decoded_token['u_id'] in channel['all_members_id']:
            messages += [message for message in channel['messages'] if query_str.lower() in message['message'].lower()]

    for dm in store['dms']:
        if decoded_token['u_id'] in dm['members']:
            messages += [message for message in dm['messages'] if query_str.lower() in message['message'].lower()]

    return {'messages': messages}