from src.auth import decode_token
import json
from src.data_store import *

'''

NOTIFICATIONS GET
Return the user's most recent 20 notifications, ordered from most recent to least recent.

Arguments
    token (str) - the encoded token of a current user that will contain their relevant info

Exceptions:
    N/A

Return Value:
   notifications
    {
        channel_id
        dm_id
        notification message
    }

'''



def notifications_get_v1(token):

    store = data_store.get()    
    
    #invalid token
    decoded_token = decode_token(store, token )
    if decoded_token['token_valid'] == False:
        raise AccessError("Token invalid")

    notifications = []

    for notif in store['notifications']:
        if notif['u_id'] == decoded_token['u_id']:
            notification = {
                'channel_id': notif['channel_id'],
                'dm_id': notif['dm_id'],
                'notification_message': notif['notification_message']
            }
            notifications.append(notification)
   
    notif_return = []
    count = 0
    for notif in notifications:
        count += 1
        notif_return.append(notif)
        if count == 20:
            break

    return {'notifications': notif_return}