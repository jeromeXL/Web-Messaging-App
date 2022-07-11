from src.data_store import data_store
from src.error import *
from src.auth import *

'''
Creates a dm directed to a list of users provided, storing the creator, members, dm name and dm_id in datastore

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    u_ids (list)            - u_ids that the dm is directed to 

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    InputError  - Occurs when a u_id in the list u_ids is not valid or is a duplicate 

Return Value:
    Returns a dictionary containing the dm_id (integer)
'''

def dm_create(token, u_ids):
    
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if len(u_ids) != len(set(u_ids)):
        raise InputError("U_ids contains duplicates")
    
    for u_id in u_ids:
        user_found = False
        for user in store['users']:
            if u_id == user['u_id']:
                user_found = True
        if user_found == False:
            raise InputError("U_id does not refer to a valid user")
    
    new_dm_id = len(store['dms']) + 1
    creator = decoded_token['u_id']
    u_ids.append(creator)
    dm_name = generate_dm_name(u_ids, store)

    new_dm = {'dm_id': new_dm_id,
                'name': dm_name,
                'creator': creator,
                'members': u_ids, 
                'messages': [],
                'messages_count': 0}
    store['dms'].append(new_dm)

    

    for u_id in u_ids:
        #find user handle
        handle_str = ''
        for user in store['users']:
            if decoded_token['u_id'] == user['u_id']:
                handle_str = user['handle_str']
        if u_id != decoded_token['u_id']:
            notif = {
                'channel_id': -1,
                'dm_id': new_dm_id,
                'notification_message': (handle_str + " added you to " + dm_name),
                'u_id': u_id
            }
            store['notifications'].append(notif)

    data_store.set(store)
    
    return {'dm_id': new_dm['dm_id']}

'''
Helper function that creates the name for a new dm

Arguments:
    store (dictionary)  - a list of information about seams stored in data store
    u_ids (list)        - u_ids that the dm is directed to 

Return Value:
    Returns a string that is the name for a new dm
'''

def generate_dm_name(u_ids, store):
    
    names = []
    for u_id in u_ids:
        for user in store['users']:
            if u_id == user['u_id']:
                names.append(user['handle_str'])
    names = sorted(names)
    dm_name = ", ".join(names)
    
    return dm_name

'''
Creates a dm directed to a list of users provided, storing the creator, members, dm name and dm_id in datastore

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    dm_id (integer)         - id of a given dm
    start (integer)         - beginning index of messages to be returned 

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session) or the user is not a member of the dm
    InputError  - Occurs when a dm_id does not refer to a valid DM or start is greater than the total number of messages 

Return Value:
    Returns a dictionary containing a list messages from index start to start + 50 (if exists), start index and end index
'''

def dm_messages(token, dm_id, start):
    
    store = data_store.get()

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    dm_found = False
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm_found = True
            dm_specific = dm
    
    if dm_found == False:
        raise InputError("dm_id does not refer to a valid DM")
    
    if decoded_token['u_id'] not in dm_specific['members']:
        raise AccessError("User not a member of the dm")

    if start > len(dm_specific['messages']):
        raise InputError("Start greater than the number of messages")
    
    # Returns up to the least recent message if there are less than (start + 50) messages 
    messages = dm_specific['messages']
    
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
Lists all dms that a user is a member of

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)

Return Value:
    Returns a list of dictionaries that contain the name and id of each dm
''' 
def dm_list_v1(token):

    store = data_store.get()
    all_dms = store['dms']
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    dm_list = []
    
    for dm in all_dms: 
        for members in dm['members']:
            if members == decoded_token['u_id']:
                dm_list.append({'dm_id': dm['dm_id'],'name': dm['name']})
        
        
    return {
        'dms': dm_list
    }

'''
Remove all info of the dm and delete the dm if done so by the owner

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    dm_id (int)             - id of the dm that is to be deleted

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    AccessError - Occurs when user is not a member of dm
    InputError  - Occurs when dm_ifd does not exist.

Return Value:
    {}
'''
def dm_remove_v1(token, dm_id):

    store = data_store.get()
    all_dms = store['dms']

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    dm_found = False
    is_member = False

    for dm in all_dms:
        if dm_id == dm['dm_id']:
            dm_found = True
            for members in dm['members']:
                if members == decoded_token['u_id']:
                    is_member = True
    
    if dm_found == False:
        raise InputError("Dm_id does not exist")
    
    if is_member == False:
        raise AccessError("You are not a member of this dm")


    
    for dm in all_dms:
        if dm['dm_id'] == dm_id:
            for members in dm['members']:
                if members == decoded_token['u_id']:
                    if dm['creator'] != decoded_token['u_id']:
                        raise AccessError("You are not the owner of this dm")
                    store['dms'].remove(dm)
                    break
    
    data_store.set(store)
    return {}

'''
Returns the details of that dm

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    dm_id (int)             - id of the dm that is to be deleted

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    AccessError - Occurs when user is not a member of dm
    InputError  - Occurs when dm_ifd does not exist.

Return Value:
    {
        name,
        members
    }
'''
def dm_details_v1(token, dm_id):

    store = data_store.get()
    all_dms = store['dms']

    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    dm_found = False
    is_member = False

    for dm in all_dms:
        if dm_id == dm['dm_id']:
            dm_found = True
            for members in dm['members']:
                if members == decoded_token['u_id']:
                    is_member = True
    
    if dm_found == False:
        raise InputError("Dm_id does not exist")
    
    if is_member == False:
        raise AccessError("You are not a member of this dm")

    member_info = []
    all_users = store['users']

    for dm in all_dms:
        if dm_id == dm['dm_id']:
            for user in all_users:
                for member_id in dm['members']:
                    if user['u_id'] == member_id:
                        member_info_dict = {"u_id": user['u_id'], "email": user['email'], "name_first": user["name_first"], "name_last": user["name_last"], "handle_str": user['handle_str']}
                        member_info.append(member_info_dict)
            name = dm['name']


    return {
        'name': name,
        'members': member_info
    }


'''
Allows user to leave specified 

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    dm_id (int)             - id of the dm that is to be deleted

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session)
    AccessError - Occurs when user is not a member of dm
    InputError  - Occurs when dm_ifd does not exist.

Return Value:
    {}
'''
def dm_leave_v1(token, dm_id):

    store = data_store.get()
    all_dms = store['dms']
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    dm_found = False
    
    is_member = False

    for dm in all_dms:
        if dm_id == dm['dm_id']:
            dm_found = True
            for members in dm['members']:
                if members == decoded_token['u_id']:
                    is_member = True
    
    if dm_found == False:
        raise InputError("Dm_id does not exist")
    
    if is_member == False:
        raise AccessError("You are not a member of this dm")


    for dm in all_dms:
        if dm['dm_id'] == dm_id:
            for members in dm['members']:
                if members == decoded_token['u_id']:
                    dm['members'].remove(members)
                    break

    return {}
