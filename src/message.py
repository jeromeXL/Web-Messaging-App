"""
Functions for message
"""

from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import datetime
#from datetime import *
from datetime import timezone
import pytz
from src.auth import *
from src.dm import *
from src.channels import *

'''
SEND MESSAGE

send a message from the authorised user to the channel
specified by channel_id 

Arguments: 
    token - token
    channel_id: (string) - channel id
    message (string) - text message

Exceptions: 
    InputError  - Occurs when the channel id does not refer to the valid channel
    InputError  - Occurs when the message is less than one character or more than 1000 characters 
    AccessError - Occurs when the channel id is valid and authorised user is not the member of channel 

Return Value: 
    {message_id} - where message_id is newly generated id  
'''


def message_send_v1(token, channel_id, message):
    """ Sends messages """
    store = data_store.get()

    if len(message) > 1000 or len(message) < 1:
        raise InputError("Message incorrect length")

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    user_id = decoded_token['u_id']

    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']


    for channel in store['channels']:

        if channel['channel_id_key'] == channel_id:
            # authorised user not a member of the channel
            for auth in channel['all_members_id']:
                if auth == user_id:
                    break
            else:
                raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

            #message_id = len(channel['messages']) + 1
            message_id = generate_message_id(store)
            reacts = {"react_id" : 1, "u_ids" : [], "is_this_user_reacted" : False}
            tagged_channel_handle_strs = []
            tagged_uids, tagged_handle_strs = check_tagging(store, message)

            for user in tagged_uids:
                notif = {
                    'channel_id': channel_id,
                    'dm_id': -1,
                    'notification_message': (handle_str + " tagged you in " + channel['name'] + ": " + message[0:20]),
                    'u_id': user
                }
                store['notifications'].insert(0, notif)

            index = 0
            for user in tagged_uids:
                for member in channel['all_members_id']:
                    if user == member:
                        tagged_channel_handle_strs.append(tagged_handle_strs[index])
                index += 1

            channel['messages'].append({'message_id': message_id, 'u_id': user_id, 'message': message, 'time_sent': str(datetime.datetime.now()), "reacts" :[reacts], "is_pinned": False, "tagged": tagged_channel_handle_strs})

            break
    else:
        # invalid channel_id
        raise InputError("channel_id does not refer to a valid channel")

    return {'message_id' : message_id}


'''
EDIT MESSAGE

edit a message 
if message is empty, delete it

Arguments: 
    token - token
    message_id: (string) - message id
    message (string) - text message

Exceptions:
    InputError  - Occurs when the message id is invalid 
    InputError  - Occurs when the message id more than 1000 characters
     
    AccessError - Occurs when the message_id is not the message the user created or user is not the owner of channel 

Return Value: 
    {}  
'''
def message_edit_v1(token, message_id, message):
    """ edits messages """
    store = data_store.get()

    if len(message) > 1000:
        raise InputError("Message incorrect length")

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    user_id = decoded_token['u_id']

    for channel in store['channels']:

        message_index = 0
        for msg in channel['messages']:

            if msg['message_id'] == message_id:
                if user_id in channel['owner_member_id'] or user_id in msg['all_members_id']:
                    break
            #message_index += 1

        # authorised user not a member of the channel or not the message owner
        else:
            raise AccessError("message_id is valid and the authorised user is not a channel owner or message owner")

        #if message == '': # delete case
            #del channel['messages'][message_index]
            #channel['messages_count'] = channel['messages_count'] - 1
        #else: # edit case
        channel['messages'][message_index]['message'] = message
        break
    else:
        # invalid message_id
        raise InputError("message_id does not refer to a valid message")

    return {}
    

'''
REMOVE MESSAGE

remove a message

Arguments: 
    token - token
    message_id: (string) - message id

Exceptions:
    InputError  - Occurs when the message id is invalid 

    AccessError - Occurs when the message_id is not the message the user created or user is not the owner of channel 

Return Value: 
    {}  
'''
def message_remove_v1(token, message_id):

    """ remove messages """
    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    user_id = decoded_token['u_id']

    for channel in store['channels']:

        message_index = 0
        for msg in channel['messages']:

            if msg['message_id'] == message_id:
                if user_id in channel['owner_member_id'] or user_id in msg['all_members_id']:
                    break
            #message_index += 1

        # authorised user not a member of the channel or not the message owner
        else:
            raise AccessError("message_id is valid and the authorised user is not a channel owner or message owner")

        del channel['messages'][message_index]
        #channel['messages_count'] = channel['messages_count'] - 1

        break
    else:
        # invalid message_id
        raise InputError("message_id does not refer to a valid message")

    return {}
    

'''
MESSAGE SENDDM

send a dm

Arguments: 
    token - token
    dm_id: (string) - dm id
    message (string) - text message

Exceptions:
    InputError  - Occurs when the dm id is invalid 
    InputError  - Occurs when the message more than 1000 characters

    AccessError - Occurs when the dm_id is valid but authorised user is not member of dm

Return Value: 
    {message_id} - where message_id is newly generated id  
'''
def message_senddm_v1(token, dm_id, message):

    """ sends dms """
    store = data_store.get()
    message_id = 0

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")


    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']
    
    user_id = decoded_token['u_id']

    if len(message) > 1000 or len(message) < 1:
        raise InputError("Message incorrect length")

    for dm in store['dms']:

        if dm['dm_id'] == dm_id:
            # authorised user not a member of the channel
            for auth in dm['members']:
                if auth == user_id:
                    break
            else:
                raise AccessError("dm_id is valid and the authorised user is not a member of the dm")

            dm['messages_count'] = dm['messages_count'] + 1
            #message_id = dm['messages_count']
            message_id = generate_message_id(store)
            reacts = {"react_id" : 1, "u_ids" : [], "is_this_user_reacted" : False}
            tagged_dm_handle_strs = []
            tagged_uids, tagged_handle_strs = check_tagging(store, message)

            for user in tagged_uids:
                notif = {
                    'channel_id': -1,
                    'dm_id': dm_id,
                    'notification_message': (handle_str + " tagged you in " + dm['name'] + ": " + message[0:20]),
                    'u_id': user
                }
                store['notifications'].insert(0, notif)
            
            index = 0
            for user in tagged_uids:
                for member in dm['members']:
                    if user == member:
                        tagged_dm_handle_strs.append(tagged_handle_strs[index])
                index += 1

            dm['messages'].append(
                {'message_id': message_id, 'u_id': user_id, 'message': message, 'time_sent': str(datetime.datetime.now()), "reacts" : [reacts], "is_pinned": False, "tagged": tagged_dm_handle_strs})

            break
    else:
        # invalid channel_id
        raise InputError("dm_id does not refer to a valid dm")

    return {'message_id': message_id}




'''
	SENDLATER - MESSAGE

	send a postponed message from the authorised user to the channel
	specified by channel_id 

	Arguments: 
    	token - token
    	channel_id: (string) - channel id
    	message (string) - text message
    	time_sent - postpone time

	Exceptions: 
    	InputError  - Occurs when the channel id does not refer to a valid channel
    	InputError  - Occurs when the message is less than one character
    	InputError  - Occurs when the message is more than 1000 characters
    	InputError  - Occurs when time_sent is a time in the past
    	AccessError - Occurs when the channel id is valid and authorised user is not a member of channel 

	Return Value: 
    	{message_id} - where message_id is newly generated id
'''

def message_sendlater_v1(token, channel_id, message, time_sent): 
    """ Sends message later """
    store = data_store.get()
    valid_time = datetime.datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()

    if len(message) > 1000 or len(message) < 1:
        raise InputError("Message incorrect length")

    if time_sent < valid_time:
    	raise InputError("Time has passed")

    decoded_token = decode_token(store, token)
    #if decoded_token['token_valid'] == False:
    #    raise AccessError("Token invalid")
    
    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']

    user_id = decoded_token['u_id']

    for channel in store['channels']:

        if channel['channel_id_key'] == channel_id:
            # authorised user not a member of the channel
            for auth in channel['all_members_id']:
                if auth == user_id:
                    break
            else:
                raise AccessError("channel_id is valid and the authorised user is not a member of the channel")



            #message_id = len(channel['messages']) + 1
            message_id = generate_message_id(store)
            reacts = {"react_id" : 1, "u_ids" : [], "is_this_user_reacted" : False}
            #time_created = time_sent
            tagged_channel_handle_strs = []
            tagged_uids, tagged_handle_strs = check_tagging(store, message)

            for user in tagged_uids:
                notif = {
                    'channel_id': channel_id,
                    'dm_id': -1,
                    'notification_message': (handle_str + " tagged you in " + channel['name'] + ": " + message[0:20]),
                    'u_id': user
                }
                store['notifications'].insert(0, notif)
            
            index = 0
            for user in tagged_uids:
                for member in channel['all_members_id']:
                    if user == member:
                        tagged_channel_handle_strs.append(tagged_handle_strs[index])
                index += 1

            channel['messages'].append({'message_id': message_id, 'u_id': user_id, 'message': message, 'time_sent': time_sent, "reacts" :[reacts], "is_pinned": False, "tagged": tagged_channel_handle_strs})

            break
    else:
        # invalid channel_id
        raise InputError("channel_id does not refer to a valid channel")

    return {'message_id' : message_id}




'''
	SENDLATERDM - MESSAGE

	send a postponed message from the authorised user to the dm
	specified by dm_id 

	Arguments: 
    	token - token
    	dm_id: (string) - dm id
    	message (string) - text message
    	time_sent - postpone time

	Exceptions: 
    	InputError  - Occurs when the dm id does not refer to a valid dm
    	InputError  - Occurs when the message is less than one character
    	InputError  - Occurs when the message is more than 1000 characters
    	InputError  - Occurs when time_sent is a time in the past
    	AccessError - Occurs when the dm id is valid and authorised user is not a member of dm

	Return Value: 
    	{message_id} - where message_id is newly generated id
'''

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """ send dm later """
    store = data_store.get()
    valid_time = datetime.datetime.now(pytz.timezone("GMT")).replace(tzinfo=timezone.utc).timestamp()
    #message_id = 0

    decoded_token = decode_token(store, token)
    #if decoded_token['token_valid'] == False:
    #    raise AccessError("Token invalid")

    user_id = decoded_token['u_id']

    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']

    if len(message) > 1000 or len(message) < 1:
        raise InputError("Message incorrect length")

    if time_sent < valid_time:
    	raise InputError("Time has passed")

    for dm in store['dms']:

        if dm['dm_id'] == dm_id:
            # authorised user not a member of the channel
            for auth in dm['members']:
                if auth == user_id:
                    break
            else:
                raise AccessError("dm_id is valid and the authorised user is not a member of the dm")

            dm['messages_count'] = dm['messages_count'] + 1
            #message_id = dm['messages_count']
            message_id = generate_message_id(store)
            reacts = {"react_id" : 1, "u_ids" : [], "is_this_user_reacted" : False}
            #time_created = time_sent
            tagged_dm_handle_strs = []
            tagged_uids, tagged_handle_strs = check_tagging(store, message)

            for user in tagged_uids:
                notif = {
                    'channel_id': -1,
                    'dm_id': dm_id,
                    'notification_message': (handle_str + " tagged you in " + dm['name'] + ": " + message[0:20]),
                    'u_id': user
                }
                store['notifications'].insert(0, notif)
            
            index = 0
            for user in tagged_uids:
                for member in dm['members']:
                    if user == member:
                        tagged_dm_handle_strs.append(tagged_handle_strs[index])
                index += 1

            dm['messages'].append(
                {'message_id': message_id, 'u_id': user_id, 'message': message, 'time_sent': time_sent, "reacts" : [reacts], "is_pinned": False, "tagged": tagged_dm_handle_strs})

            break
    else:
        # invalid channel_id
        raise InputError("dm_id does not refer to a valid dm")

    return {'message_id': message_id}



'''
SHARE MESSAGE

Share a message from a dm or channel that the user is part of to another
dm or channel that they are also a part of 

Arguments: 
    token (string)                  - token
    og_message_id (integer)         - message_id of a message in a dm or channel
    message (string)                - optional message is being added to the original message
    channel_id (integer)            - if sharing to a channel, the id of that channel. -1 otherwise
    dm_id (integer)                 - if sharing to a dm, the id of that dm. -1 otherwise

Exceptions: 
    InputError  - Occurs when both channel_id and dm_id are invalid, neither channel_id or dm_id is -1,
                    og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined,
                    or the length of the message is more than 1000 characters
    AccessError - Occurs when the token given is invalid or the pair of channel_id and dm_id are valid and the authorised user 
                    has not joined the channel or DM they are trying to share the message to

Return Value: 
    Returns a dictionary containing the new id of the shared message
'''

def message_share(token, og_message_id, message, channel_id, dm_id):

    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if len(message) > 1000:
        raise InputError("Length of message is greater than 1000 characters")

    channel_found = False
    dm_found = False
    message_found = False
    new_message = message
    for channel in store['channels']:
        for msg in channel['messages']:
            if og_message_id == msg['message_id'] and decoded_token['u_id'] in channel['all_members_id']:
                message_found = True
                new_message += msg['message']
        if channel_id == channel['channel_id_key']:
            channel_found = True
            new_channel = channel
    for dm in store['dms']:
        for msg in dm['messages']:
            if og_message_id == msg['message_id'] and decoded_token['u_id'] in dm['members']:
                message_found = True
                new_message += msg['message']
        if dm_id == dm['dm_id']:
            dm_found = True
            new_dm = dm

    if message_found == False:
        raise InputError("og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    if channel_found == False and dm_found == False:
        raise InputError("Both channel_id and dm_id are invalid")
    if channel_found == True and dm_found == True:
        raise InputError("Both channel_id and dm_id are valid")

    if channel_found and decoded_token['u_id'] not in new_channel['all_members_id']:
        raise AccessError("User has not joined the channel they are trying to share the message to")
    if dm_found and decoded_token['u_id'] not in new_dm['members']:
        raise AccessError("User has not joined the dm they are trying to share the message to")

    if channel_found:
        shared_message = message_send_v1(token, channel_id, new_message)
    if dm_found:
        shared_message = message_senddm_v1(token, dm_id, new_message)

    data_store.set(store)

    return {'shared_message_id': shared_message['message_id']}


'''
MESSAGE REACT

Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.

Arguments:
    token (string)          - token
    message_id (int)        - message_id of a message in a dm or channel
    react_id (int)          - id of the react
    
Exceptions:
    Input error(s):         
                            - message_id is not a valid message within a channel or DM that the authorised user has joined
                            - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
                            - the message already contains a react with ID react_id from the authorised user
    Access error(s):
                            -invalid token is passed in

Return Value:
    {}       
    
'''
def message_react_v1(token, message_id, react_id):  

    store = data_store.get()

    decoded_token = decode_token(store, token)

    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if react_id != 1:
        raise InputError("react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1")

    contains = False
    notif = {}
    #find user handle
    handle_str = ''
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            handle_str = user['handle_str']


    for channel in store['channels']:
        if decoded_token['u_id'] in channel['all_members_id']:
            
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    contains = True
                    if decoded_token['u_id'] in message['reacts'][0]['u_ids']:
                        raise InputError("the message already contains a react with ID react_id from the authorised user")
                    message['reacts'][0]['u_ids'].append(decoded_token['u_id'])
                    message['reacts'][0]['is_this_user_reacted'] = True
                    message_owner = message['u_id']
                    notif = {
                        'channel_id': channel['channel_id_key'],
                        'dm_id': -1,
                        'notification_message': (handle_str + " reacted to your message in " + channel['name']),
                        'u_id': message_owner
                    }
    
    
    for dm in store['dms']:
        if decoded_token['u_id'] in dm['members']:
            for dm_message in dm['messages']:
                if dm_message['message_id'] == message_id:
                    contains = True
                    if decoded_token['u_id'] in dm_message['reacts'][0]['u_ids']:
                        raise InputError("the message already contains a react with ID react_id from the authorised user")
                    dm_message['reacts'][0]['u_ids'].append(decoded_token['u_id'])
                    dm_message['reacts'][0]['is_this_user_reacted'] = True
                    message_owner = dm_message['u_id']
                    notif = {
                        'channel_id': -1,
                        'dm_id': dm['dm_id'],
                        'notification_message': (handle_str + " reacted to your message in " + dm['name']),
                        'u_id': message_owner
                    }

    if notif != {}:
        store['notifications'].insert(0, notif)


    if contains == False:
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    data_store.set(store)

    return {}

'''
MESSAGE UNREACT

Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.
    
Arguments:
    token (string)          - token
    message_id (int)        - message_id of a message in a dm or channel
    react_id (int)          - id of the react

Exceptions:
    Input error(s):         
                            - message_id is not a valid message within a channel or DM that the authorised user has joined
                            - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
                            - the message does not contain a react with ID react_id from the authorised user
    Access error(s):
                            -invalid token is passed in

Return Value:
    {}       

'''
def message_unreact_v1(token, message_id, react_id):  

    store = data_store.get()

    decoded_token = decode_token(store, token)

    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if react_id != 1:
        raise InputError("react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1")

    contains = False

    for channel in store['channels']:
        if decoded_token['u_id'] in channel['all_members_id']:
            
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    contains = True
                    if decoded_token['u_id'] not in message['reacts'][0]['u_ids']:
                        raise InputError("the message does not contain a react with ID react_id from the authorised user")
                    message['reacts'][0]['u_ids'].remove(decoded_token['u_id'])
                    message['reacts'][0]['is_this_user_reacted'] = False
    
    for dm in store['dms']:
        if decoded_token['u_id'] in dm['members']:
            for dm_message in dm['messages']:
                if dm_message['message_id'] == message_id:
                    contains = True
                    if decoded_token['u_id'] not in dm_message['reacts'][0]['u_ids']:
                        raise InputError("the message does not contain a react with ID react_id from the authorised user")
                    dm_message['reacts'][0]['u_ids'].remove(decoded_token['u_id'])
                    dm_message['reacts'][0]['is_this_user_reacted'] = False

    if contains == False:
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    data_store.set(store)

    return {}
                        
'''
Generates a unique message_id

Arguments:
    store (dictionary)  - data store that contains all information stored related to seams 

Return Value:
    An integer message_id
'''

def generate_message_id(store):

    message_id = 1

    for channel in store['channels']:
        message_id += len(channel['messages'])
    for dm in store['dms']:
        message_id += len(dm['messages'])

    return message_id




'''
MESSAGE PIN

Given a message within a channel or DM, mark it as "pinned".

Arguments:
    token (string)          - token
    message_id (int)        - message_id of a message in a dm or channel
    
Exceptions:
    Input error(s):         
                            - message_id is not a valid message within a channel or DM that the authorised user has joined
                            - the message is already pinned
    Access error(s):
                            -invalid token is passed in

Return Value:
    {}       
    
'''
def message_pin_v1(token, message_id):  

    store = data_store.get()

    decoded_token = decode_token(store, token)

    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    contains = False

    #channels
    for channel in store['channels']:
        if decoded_token['u_id'] in channel['all_members_id']:
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    contains = True
                    if message["is_pinned"] == True:
                        raise InputError("the message is already pinned")
                    message["is_pinned"] = True
    
    #dms
    for dm in store['dms']:
        if decoded_token['u_id'] in dm['members']:
            for dm_message in dm['messages']:
                if dm_message['message_id'] == message_id:
                    contains = True
                    if dm_message['is_pinned'] == True:
                        raise InputError("the message is already pinned")
                    dm_message['is_pinned'] = True

    if contains == False:
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    data_store.set(store)

    return {}


'''
MESSAGE UNPIN

Given a message within a channel or DM the authorised user is part of, remove a pin to that particular message.
    
Arguments:
    token (string)          - token
    message_id (int)        - message_id of a message in a dm or channel

Exceptions:
    Input error(s):         
                            - message_id is not a valid message within a channel or DM that the authorised user has joined
                            - the message is not pinned from the authorised user
    Access error(s):
                            -invalid token is passed in

Return Value:
    {}       

'''
def message_unpin_v1(token, message_id):

    store = data_store.get()

    decoded_token = decode_token(store, token)

    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    contains = False

    for channel in store['channels']:
        if decoded_token['u_id'] in channel['all_members_id']:
            
            for message in channel['messages']:
                if message['message_id'] == message_id:
                    contains = True
                    if message["is_pinned"] == False:
                        raise InputError("the message is not pinned")
                    message['is_pinned'] = False
    
    for dm in store['dms']:
        if decoded_token['u_id'] in dm['members']:
            for dm_message in dm['messages']:
                if dm_message['message_id'] == message_id:
                    contains = True
                    if dm_message["is_pinned"] == False:
                        raise InputError("the message is not pinned")
                    dm_message['is_pinned'] = False

    if contains == False:
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    data_store.set(store)

    return {}

'''
CHECK TAGGING

Given a message within a channel or DM the authorised user is part of, check if a user(s) are tagged in the message
    
Arguments:
    store (dictionary)  - data store that contains all information stored related to seams 
    message (string)    - the message that may contain a tagged user

Exceptions:
    NA

Return Value:
    Two list which each contain the u_ids and the handle strings of all of the tagged users. They are empty if no users are tagged       

'''

def check_tagging(store, message):

    tagged_uids = []
    tagged_handle_strs = []
    for user in store['users']:
        handle = '@' + user['handle_str']
        if handle in message:
            split_message = message.split(handle, 1)
            if split_message[1] == '' or split_message[1][0].isalnum() == False:
                tagged_uids.append(user['u_id'])
                tagged_handle_strs.append(user['handle_str'])
    tagged_uids = sorted(tagged_uids)
    tagged_handle_strs = sorted(tagged_handle_strs)

    return tagged_uids, tagged_handle_strs