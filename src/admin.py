
#remove from channels, dms, not in users/all, 
# seams owners can remove other owners,
#contents of messages replaced by removed user, 
# profile must be retrievable with user/profile but name first = removed and name last = user
#users email and handle should be reusable
#from asyncio.windows_events import NULL
from src.data_store import data_store
from src.error import*
#from src.error import InputError
from src.auth import *
from src.channels import *
from src.dm import *
from src.channel import*


"""
ADMIN USER REMOVE:
Given a user by their u_id, remove them from the Seams. This means they should be removed from all channels/DMs, 
and will not be included in the list of users returned by users/all. Seams owners can remove other Seams owners 
(including the original first owner). Once users are removed, the contents of the messages they sent will be replaced 
by 'Removed user'. Their profile must still be retrievable with user/profile, however name_first should be 'Removed'
and name_last should be 'user'. The user's email and handle should be reusable.

Arguments:
    token (string)   - An authorisation hash that is valid if a user is logged in
    u_id (integer)    - The user ID of the person being invited

Exceptions:
    InputError - u_id does not refer to a valid user
    InputError - u_id refers to a user who is the only global owner
    AccessError - the authorised user is not a global owner
    AccessError - Invalid Token

      

"""

def admin_user_remove_v1(token, u_id):

    store = data_store.get()
    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    #authorised user is not a global owner
    for auth_user in store['users']:
        if auth_user['u_id'] == decoded_token['u_id']:
            if auth_user['permission_id'] != 1:
                raise AccessError("the authorised user is not a global owner")
            #break
    
    u_id_permissions = -1
    #invalid u_id
    for user in store['users']:
        if user['u_id'] == u_id:
            u_id_permissions = user['permission_id']
            break
    else:
        raise InputError("u_id does not refer to a valid user")

    counter = 0

    
    for user1 in store['users']:
        if user1['permission_id'] == 1:
            counter = counter+1
    
    #u_id is the only global owner
    if counter == 1 and u_id_permissions == 1:
        raise InputError("u_id refers to a user who is the only global owner")

    
    #invalidate token
    for user3 in store['users']:
        if user3['u_id'] == u_id:
            user3['session_list'].clear()
    
    
    #change name to "Removed User" and gets rid of their email and handle string
    for user2 in store['users']:
        if user2['u_id'] == u_id:
            user['name_first'] = "Removed"
            user['name_last'] = "user"
            user['email'] = ""
            user['handle_str'] = ""

    
    #remove from channel
    
    for channel in store['channels']:
        
        for message1 in channel['messages']:
            if message1['u_id'] == u_id:
                message1['message'] = "Removed user"
        
        
        for member1 in channel['all_members_id']:
            if member1 == u_id:
                channel['all_members_id'].remove(u_id)
        
        
        for owner_member in channel['owner_member_id']:
            if owner_member == u_id:
                channel['owner_member_id'].remove(u_id)
        
    
    #remove from dm
    for dm in store['dms']:
        for message in dm['messages']:
            if message['u_id'] == u_id:
                message['message'] = "Removed user"
        for member in dm['members']:
            if member == u_id:
                dm['members'].remove(u_id)
    
        if dm['creator'] == u_id:
            dm['members'].remove(u_id)
    
    data_store.set(store)



        

from src.data_store import data_store
from src.error import *
from src.auth import *

'''
Changes the permission id of a given user 

Arguments:
    token (string)          - an authorisation hash that is valid if a user is logged in
    u_id (integer)          - the u_id of the users who's permission id you want to change 
    permission_id (integer) - the permission_id you want to change to 

Exceptions:
    AccessError - Occurs when an invalid token is given (invalid user_id or user_session) 
                    or the authorised user is not a global owner
    InputError  - Occurs when u_id does not refer to a valid user, u_id refers to the only global owner
                    who is being demoted, permission_id is invalid or the user already has the given
                    permission_id

Return Value:
    Returns an empty dictionary
'''

def admin_userpermission_change(token, u_id, permission_id):
    
    store = data_store.get()
    
    decoded_token = decode_token(store, token)
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    if permission_id != 1 and permission_id != 2:
        raise InputError("Permission id invalid")

    global_owners = 0
    user_found = False
    for user in store['users']:
        if decoded_token['u_id'] == user['u_id']:
            if user['permission_id'] != 1:
                raise AccessError("Authorised user not a global owner")
        if u_id == user['u_id']:
            user_found = user
            if user['permission_id'] == permission_id:
                raise InputError("User already has the premission levels of permission_id")
        if user['permission_id'] == 1:
            global_owners += 1
    
    if user_found == False:
        raise InputError("U_id does not refer to a valid user")

    if global_owners == 1 and user_found['permission_id'] == 1:
        raise InputError("U_id refers to a user who is the only global owner and they are being demoted to a user")

    user_found['permission_id'] = permission_id

    data_store.set(store)
    
    return {}
