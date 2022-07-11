
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import threading, time
import datetime 
from datetime import timezone
from src.auth import *
from src.message import *
#from datetime import datetime, timedelta 

'''
STANDUP START

For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" with a message, it is buffered during the X second window then at the end of the X second window a message will be added to the message queue in the channel from the user who started the standup. "length" is an integer that denotes the number of seconds that the standup occurs for. If no standup messages were sent during the duration of the standup, no message should be sent at the end.

Arguments:
    token(string)       - an authorisation hash that is valid if a user is logged in
    channel_id(int)     - the id of a channel
    length(int)         - the length of time the standup will run for

Exceptions:
    Input Error:
        - channel_id does not refer to a valid channel
        - length is a negative integer
        - an active standup is currently running in the channel

    Access Error:
        - channel_id is valid and the authorised user is not a member of the channel
        - the token passed in is invalid
    
Returns:
    {time_finish}
    time_finish is when the standup finishes. 

'''


def standup_start_v1(token, channel_id, length):
    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if length < 0:
        raise InputError("Length not valid")

    channel_found = False

    for channel in store['channels']:
        if channel['channel_id_key'] == channel_id:
            channel_found = True
            channel_standup = channel
    
    if channel_found == False:
        raise InputError("Channel not found")

    if decoded_token['u_id'] not in channel_standup['all_members_id']:
        raise AccessError("You are not a member of this channel")
    '''
    if standup_active_v1(token, channel_id)['is_active']:
        raise InputError("A standup is already running")
    '''

    current_time = datetime.datetime.now()
    time_finish = int(current_time.strftime("%s")) + length
    # add to channel

    new_stand_up = {
        'channel_id_key': channel_id,
        'time_finish': time_finish,
        'messages': []
    }
    store['standups'].append(new_stand_up)
    
    threading.Timer(length, standup_sending, args=(decoded_token['u_id'], channel_id)).start()

    return {
        'time_finish': time_finish
    }

'''
STANDUP ACTIVE

For a given channel, return whether a standup is active in it, and what time the standup finishes. If no standup is active, then time_finish returns None

Arguments:
    token(string)       - an authorisation hash that is valid if a user is logged in
    channel_id(int)     - the id of a channel

Exceptions:
    Input Error:
        - channel_id does not refer to a valid channel

    Access Error:
        - channel_id is valid and the authorised user is not a member of the channel
        - the token passed in is invalid
    
Returns:
    {is_active, time_finish}
    where is_active a boolean value and time_finish is when the standup finishes. 
    If there is no standup time_finish returns 'None'

'''

def standup_active_v1(token, channel_id):

    store = data_store.get()
    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    current_time = datetime.datetime.now()
    timenow = int(current_time.strftime("%s"))
    
    is_active = False
    time_finish = None
    channel_found = False

    for channel in store['channels']:
        if channel['channel_id_key'] == channel_id:
            channel_found = True
            if decoded_token['u_id'] not in channel['all_members_id']:
                raise AccessError("channel_id is valid and the authorised user is not a member of the channel")
            
    
    if channel_found == False:
        raise InputError("channel_id does not refer to a valid channel")

    for standup in store['standups']:
        if standup['channel_id_key'] == channel_id and standup['time_finish'] > timenow:
            is_active = True
            time_finish = standup['time_finish']

    
    return {"is_active" : is_active,
            "time_finish" : time_finish}


def standup_sending(token, channel_id):
    store = data_store.get()

    decoded_token = decode_token(store, token)

    message = ''
    for index, stand_up in enumerate(store['stand_ups']):
        if stand_up['channel_id'] == channel_id:
            standup_current = store['stand_ups'].pop(index)
            message = "\n".join(standup_current['messages'])
    
    current_time = datetime.datetime.now()
    time_started = int(current_time.strftime("%s"))

    if message != '':
        for channel in store['channels']:
            if channel["channel_id_key"] == channel_id:
                message_id = generate_message_id(store)
                reacts = {"react_id" : 1, "u_ids" : [], "is_this_user_reacted" : False}
                channel['messages'].append(
                    {
                        'message_id': message_id, 
                        'u_id': decoded_token['u_id'], 
                        'message': message, 
                        'time_created': time_started,
                        "reacts" :[reacts]
                    }
                )



'''
	SEND - STANDUP

	send a message from the authorised user to the standup queue
	assuming standup is active

	Arguments: 
    	token - token
    	channel_id: (string) - channel id
    	message (string) - text message

	Exceptions: 
    	InputError  - Occurs when the channel id does not refer to a valid channel
    	InputError  - Occurs when the message is less than one character
    	InputError  - Occurs when the message is more than 1000 characters
    	InputError  - Occurs when active standup is not running
    	AccessError - Occurs when the channel id is valid and authorised user is not a member of channel

	Return Value: 
    	{}
'''

def standup_send_v1(token, channel_id, message):
    """ send message to standup """
    store = data_store.get()

    if len(message) > 1000:
        raise InputError("Message incorrect length")

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    #if not standup_active_v1(token, channel_id)['is_active']:
    #	raise InputError("Standup is not active")

    user_id = decoded_token['u_id']
    #user_name = user_id.get('name_first')

    for channel in store['channels']:

        if channel['channel_id_key'] == channel_id:
            # authorised user not a member of the channel
            for auth in channel['all_members_id']:
                if auth == user_id:
                    break
            else:
                raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

            store['standups'].append(f"{user_id}: {message}")

            break
    else:
        # invalid channel_id
        raise InputError("channel_id does not refer to a valid channel")

    return {}
