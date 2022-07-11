from base64 import decode
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.auth import *
from src.other import *
from src.user import *

'''
CHANNELS CREATE
  
Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins the channel 

Arguments: 
    auth_user_id (integer) - this is the user id that is checked in the datastore  
    name (string) - this is the name that will be assigned to the channel 
    is_public (Boolean) - True means the channel is public, False means it is private 

Exceptions: 
    InputError  - Occurs when the name is less than one character or more than 20 characters 
    AccessError - Occurs when the auth_user_id isn't found in the datastore 

Return Value: 
    channel_id (integer) - a newly generated id that is specific to that channel  
'''

def channels_create_v1(token, name, is_public):
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")


    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    #Checking 1<name<20characters
    if len(name) < 1:
        raise InputError("Name is empty")
    if len(name) > 20:
        raise InputError("Name is too long")
    
    #Assigning new channel ID

    new_channel_id = len(store['channels']) + 1

  
    #Adding new channel to the data store 
    
    new_channel = {'channel_id_key': new_channel_id, 'owner_member_id': [decoded_token['u_id']], 'all_members_id': [decoded_token['u_id']], 'name': name, 'is_public': is_public, 'messages': []}

    store['channels'].append(new_channel)

    data_store.set(store)
    
    return {
        'channel_id': new_channel_id,
    }

'''
CHANNELS LISTALL

    A list of all channels, including private channels, (and their associated details) 

Arguments: 
    auth_user_id (int)    -  this is the user id that is checked in the datastore 

 Exceptions: 
    InputError  - N/A 
    AccessError - Occurs when the auth_user_id isn't found in the datastore 

Return Value: 
    Returns Channels, which is a list of dictionaries that contain: 
        - Channel_id_key  
        - Owner_member_id 
        - All_members_id 
        - Name 
        - Is_public 

'''

#def channels_listall_v1(auth_user_id):
def channels_listall_v1(token):
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    '''
    user_exist = False
    for user in store['users']:
        if auth_user_id == user['u_id']:
            user_exist = True
    if not user_exist:
        raise AccessError
    '''
    
    datastore_channel_list = store['channels']
    return_channels_list = []
    
    for channel_row in datastore_channel_list: 
        return_channels_list.append({'channel_id': channel_row['channel_id_key'],'name': channel_row['name']})

        
    return {
        'channels': return_channels_list
    }

    
'''
CHANNELS LIST

Provide a list of all channels (and their associated details) that the authorised user is part of. 

Arguments: 
    auth_user_id (int) -  this is the user id that is checked in the datastore 

Exceptions: 
    InputError  - N/A 
    AccessError - Occurs when the auth_user_id isn't found in the datastore

Return Value: 
    Returns Channels, which is a list of dictionaries that contain: 
        -Channel_id_key  
        -Owner_member_id 
        -All_members_id 
        -Name 
        -Is_public 


'''
    
#def channels_list_v1(auth_user_id):
def channels_list_v1(token):
    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    auth_user_id = decoded_token['u_id']
    
    '''
    user_check = False
    for user in store['users']:
        if auth_user_id == user['u_id']:
            user_check = True
    if not user_check: 
        raise AccessError
    '''
    
    datastore_channel_list = store ['channels']
    return_channels_list = [] 
    
    for channel_row in datastore_channel_list: 
        if auth_user_id in channel_row['all_members_id']:
            return_channels_list.append({'channel_id': channel_row['channel_id_key'],'name': channel_row['name']})

    return {
        'channels': return_channels_list
    }







