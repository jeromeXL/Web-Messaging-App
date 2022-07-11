"""
Functions for channel.py
"""
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
#from src.error import InputError
from src.auth import *
from src.channels import *
#from src.auth import decode_token


'''
CHANNEL INVITE

Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately. 
In both public and private channels, all members are able to invite users.

Arguments:
    token (string)   - An authorisation hash that is valid if a user is logged in
    channel_id (integer)    - The ID of the channel
    u_id (integer)          - The user ID of the person being invited

Exceptions:
   InputError - channel_id does not refer to a valid channel
   InputError - u_id does not refer to a valid user
   InputError - u_id refers to a user who is already a member of the channel
   AccessError - channel_id is valid and the authorised user is not a member of the channel
   AccessError - The token is invalid

Return Value:
    {}
'''


def channel_invite_v2(token, channel_id, u_id):
    
    """ invite """
    store = data_store.get()    
    
    #invalid token
    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")


   
    #invalid u_iud
    for user in store['users']:
        if user['u_id'] == u_id:
            break
    else:
        raise InputError("u_id does not refer to a valid user")

    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']

    for channel in store['channels']:
        if channel['channel_id_key'] == channel_id:
            #user already in channel
            if u_id in channel['all_members_id']:    
                raise InputError("u_id refers to a user who is already part of the channel")
            #authorised user not a member of the channel
            for auth in channel['all_members_id']:
                if auth == decoded_token['u_id']:
                    break
            else:
                raise AccessError("channel_id is valid and the authorised user is not a member of the channel")
            channel['all_members_id'].append(u_id)
            notif = {
                'channel_id': channel_id,
                'dm_id': -1,
                'notification_message': (handle_str + " added you to " + channel['name']),
                'u_id': u_id
            }
            store['notifications'].insert(0, notif)
            break
    else:
        #invalid channel_id
        raise InputError("channel_id does not refer to a valid channel")
 
    return {
    }

'''
CHANNEL DETAILS

Function will return a dictionary of details from a given channel that a user is a member of, including the channel name, whether it is public or private and information of the owners and members. It will not return private data such as passwords

Arguments
    token (str) - the encoded token of a current user that will contain their relevant info
    Channel_id (int) - the channel id of the channel the user is trying to access details about.

Exceptions:
    InputError - Occurs when channel id does not correspond to an existing channel.
    AccessError - Occurs if user is not a member of the channel.
    AccessError - the token passed in is invalid


Return Value:
    Returns details_to_return on successfully creating a dictionary of the data from a channel.
    {
        channel name
        public or not
        owner members
        all members
    }



'''
def channel_details_v1(token, channel_id):

    """ details """
    store = data_store.get()
    
    channel_found = False
    user_id_found = False

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    # Checks if channel is found and valid and if user is a member of the channel
    for channel in store['channels']:
        if channel_id == channel['channel_id_key']:
            channel_info = channel
            channel_found = True
            for members in channel['all_members_id']:
                if members == decoded_token['u_id']:
                    user_id_found = True
            if user_id_found == False:
                raise AccessError("You are not a member of this channel")

    if channel_found == False:
        raise InputError("Channel not found")

    # Store 
    owner_members_info = []
    for index in channel_info['owner_member_id']:
        for user in store['users']:
            if user["u_id"] == index:
                new_owner_info = {
                    "u_id": user['u_id'],
                    "email": user['email'],
                    "name_first": user["name_first"],
                    "name_last": user["name_last"],
                    "handle_str": user['handle_str']
                    }
                owner_members_info.append(new_owner_info)

    all_member_info = []
    
    for index in channel_info['all_members_id']:      
        for user in store['users']:        
            if user["u_id"] == index:
                new_all_member_info = {
                    "u_id": user['u_id'],
                    "email": user['email'],
                    "name_first": user["name_first"],
                    "name_last": user["name_last"],
                    "handle_str": user['handle_str']
                    }
                all_member_info.append(new_all_member_info)

    details_to_return = {
        "name" : channel_info["name"],
        "is_public": channel_info["is_public"],
        "owner_members": owner_members_info,
        "all_members": all_member_info
        } 


    return details_to_return

'''
CHANNEL MESSAGES

Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages.

Arguments:
    token (str) - The token of user of the user who is making the request
    channel_id (integer) -  The ID of the channel
    start (integer) - start of the messages

Exceptions:
    InputError - channel_id does not refer to a valid channel
    InputError - start is greater than the total number of messages in the channel
    AccessError - channel_id is valid and the authorised user is not a member of the channel
    AccessError - The auth_user_id is invalid

Returns:
    {messages, start, end} 
    - list of messages
'''


def channel_messages_v2(token, channel_id, start):
    """ message """

    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    user_id = decoded_token['u_id']

    channel_found = False
    channels = store['channels']
    for channel in channels:
        if channel['channel_id_key'] == channel_id:
            channel_found = True
            if user_id not in channel['all_members_id']:
                raise AccessError()
            messages = channel['messages']
            
    if channel_found == False:
        raise InputError("channel_id does not refer to a valid channel")

    if start > len(messages):
        raise InputError("Start greater than the number of messages")

    for message in messages:
        if decoded_token['u_id'] in message['reacts'][0]['u_ids']:
            message['reacts'][0]['is_this_user_reacted'] = True
        else:
            message['reacts'][0]['is_this_user_reacted'] = False
            
    reversed_messages = list(reversed(messages))
    end = start + 50
    if end < len(messages):
        reversed_messages = reversed_messages[start: end]
    else:
        reversed_messages = reversed_messages[start: ]
        end = -1

    return { 'messages': reversed_messages,
            'start': start,
            'end': end}
'''
CHANNEL JOIN

Given a channel_id of a channel that the authorised user can join, adds them to that channel.

Arguments:
    token (string) - An authorisation hash that is valid if a user is logged in
    channel_id (integer - The ID of the channel

Exceptions:
    InputError - channel_id does not refer to a valid channel
    InputError - the authorised user is already a member of the channel
    AccessError - channel_id refers to a channel that is private and the authorised user is not already a channel member 
                  and is not a global owner
    AccessError - The token is invalid

Returns:
{}

'''

def channel_join_v2(token, channel_id):

    """ join """
    store = data_store.get()    
    user_permissions = -1

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")
    
    #invalid auth_user_id
    for auth_user in store['users']:
        if auth_user['u_id'] == decoded_token['u_id']:
            user_permissions = auth_user['permission_id']


    for channel in store['channels']:
        if channel['channel_id_key'] == channel_id:
            #user already in channel
            for auth in channel['all_members_id']:
                if auth == decoded_token['u_id']:
                    raise InputError("the authorised user is already a member of the channel")
            #authorised user not a member of the channel
            if channel['is_public'] == False and user_permissions != 1:
                raise AccessError("channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner")
            channel['all_members_id'].append(decoded_token['u_id'])
            break
    else:
        #invalid channel_id
        raise InputError("channel_id does not refer to a valid channel")

    return {
    }



'''
CHANNEL LEAVE
Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel. Their messages should remain in the channel.
If the only channel owner leaves, the channel will remain

Arguments:
    token (string) - a JSON Web Token
    channel_id
    ...

Exceptions:
    InputError  - channel_id does not refer to a channel
    AccessError - channel_id is valid but not a member of the channel

Return Value:
    Returns () - an empty dictionary
'''

def channel_leave_v1(token, channel_id):
    store = data_store.get()
    decoded_token = decode_token(store, token)
    
    if not decoded_token['token_valid']:
        raise AccessError("Token Invalid")
    
    auth_user_id = decoded_token['u_id']
    
    channel_exist = False 
    authorised_member = False 
    
    for channel_row in store['channels']:
        if channel_id == channel_row['channel_id_key']:
            channel_exist = True
            if auth_user_id in channel_row['all_members_id']:
                channel_row['all_members_id'].remove(auth_user_id)
                authorised_member = True
            if auth_user_id in channel_row['owner_member_id']:
                channel_row['owner_member_id'].remove(auth_user_id)
                authorised_member = True
            data_store.set(store)
            #return{}
    
    if not channel_exist:
        raise InputError("Invalid Channel")
    
    if not authorised_member:
        raise AccessError("No permission in Channel")
            
    return{}
'''
CHANNEL ADDOWNER
Makes user with user u_id an owner of the channel 

Arguments:
    token (string) - a JSON Web Token
    channel_id
    u_id - user id to be added to the owner member list
    ...

Exceptions:
    InputError  - 
        channel_id does not refer to a channel, 
        u_id does not refer to valid user, 
        u_id refers to user who is not a member of the channel 
        u_id refers to user who is already an owner of the channel
    AccessError - channel_id is valid but not a member of the channel

Return Value:
    Returns () - an empty dictionary
'''

def channel_addowner_v1(token, channel_id, u_id):
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    
    if not decoded_token['token_valid']:
        raise AccessError("Token Invalid")
    
    auth_user_id = decoded_token['u_id']
    
    channel_exist = False 
    valid_user = False 
    permissions = -1
    datastore_user_list = store['users']
    for user_row in datastore_user_list:
        if u_id == user_row['u_id']:
            valid_user = True 
        if auth_user_id == user_row['u_id']:
            permissions = user_row['permission_id']
      
    
    if not valid_user:
        raise InputError("New owner is not a valid user")
    
    for channel_row in store['channels']:
        if channel_id == channel_row['channel_id_key']:
            channel_exist = True 
            if auth_user_id not in channel_row['owner_member_id'] and permissions != 1:
                raise AccessError("No permission in Channel")
            if u_id not in channel_row['all_members_id']:
                raise InputError("User not a member of the channel")
            if u_id in channel_row['owner_member_id']:
                raise InputError("User already an owner of the channel")
            channel_row['owner_member_id'].append(u_id)
            data_store.set(store)
            return {}
        
    if not channel_exist:
        raise InputError("Invalid Channel")
        
        
'''
CHANNEL REMOVEOWNER
Removes user with user id u_id as an owner of the channel 

Arguments:
    token (string) - a JSON Web Token
    channel_id
    u_id - user id to be removed from the owner member list
    ...

Exceptions:
    InputError  - 
        channel_id does not refer to a channel, 
        u_id does not refer to valid user, 
        u_id refers to user who is not an owner of the channel 
        u_id refers to user who is the only owner of the channel
    AccessError - channel_id is valid but is not an owner of the channel

Return Value:
    Returns () - an empty dictionary
'''


def channel_removeowner_v1(token, channel_id, u_id):
    #print("jerome################################")
    #print("\n")
    store = data_store.get()
    decoded_token = decode_token(store, token)
    
    if not decoded_token['token_valid']:
        raise AccessError("Token Invalid")
    
    auth_user_id = decoded_token['u_id']
    
    channel_exist = False
    valid_user = False 
    permissions = -1 
    datastore_user_list = store['users']
    
    for user_row in datastore_user_list:
        if u_id == user_row['u_id']:
            valid_user = True
        if auth_user_id == user_row['u_id']:
            permissions = user_row['permission_id']
    if not valid_user:
        raise InputError("New owner is not a valid user")
    
    for channel_row in store['channels']:
        if channel_id == channel_row['channel_id_key']:
            channel_exist = True 
            if auth_user_id not in channel_row['owner_member_id'] and permissions != 1:
                raise AccessError("No permission in Channel")
            if u_id not in channel_row['owner_member_id']:
                raise InputError("User not an owner of the channel")
            if len(channel_row['owner_member_id']) == 1:
                raise InputError("User is the only owner of the channel")
            
            channel_row['owner_member_id'].remove(u_id)
            data_store.set(store)
            return{}
        
    if not channel_exist:
        raise InputError("Invalid Channel")





       
        
        

