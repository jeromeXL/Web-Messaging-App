from crypt import methods
import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
#from src.error import InputError
from src import config
from flask_mail import Mail, Message
from datetime import datetime



from src.auth import *
from src.other import *
from src.user import *
from src.dm import *
from src.channel import *
from src.channels import *
from src.message import *
from src.standup import *
from src.notifications import *

from src.admin import*
from src.search import *
from src.standup import *


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

mail= Mail(APP)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'groupant1531@gmail.com'
APP.config['MAIL_PASSWORD'] = 'Comp1531GroupAnt'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

# Example

@APP.route("/echo", methods = ['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "eccho')
    return dumps({
        'data': data
    })

############################################## CHANNEL ROUTES ############################################## 

#channel join
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    channel_id = data['channel_id']
    token = data['token']
    channel_join_v2(token, int(channel_id))
    return dumps({})

#channel invite 
@APP.route("/channel/invite/v2", methods = ['POST'])
def channel_invite():
    data = request.get_json()
    channel_id = data['channel_id']
    token = data['token']
    u_id = data['u_id']
    channel_invite_v2(token, int(channel_id), int(u_id))
    return dumps ({})

#channel details
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    token = request.args.get('token', None)
    channel_id = request.args.get('channel_id', None)
    return dumps(channel_details_v1(token, int(channel_id)))

#channels create
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    request_data = request.get_json()
    return dumps(channels_create_v1(request_data['token'], request_data['name'], request_data['is_public']))

#channel listall
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    token = request.args.get('token')
    return dumps(channels_listall_v1(token))

#channel list
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    return dumps(channels_list_v1(token))

# channel leave
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v0():
    request_data = request.get_json()
    return dumps(channel_leave_v1(request_data['token'], request_data['channel_id']))

#channel add owner
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner_v0():
    request_data = request.get_json()
    return dumps(channel_addowner_v1(request_data['token'], request_data['channel_id'], request_data['u_id']))

#channel remove owner
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_v0():
    request_data = request.get_json()
    return dumps(channel_removeowner_v1(request_data['token'], request_data['channel_id'], request_data['u_id']))

#channel message
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2_get():
	token, channel_id, start = request.args.get('token', None), request.args.get('channel_id', None), request.args.get('start', None)
	return dumps(channel_messages_v2(token, int(channel_id), int(start)))
 

############################################## USER ROUTES ############################################## 

#user profile setname
@APP.route("/user/profile/setname/v1", methods = ['PUT'])
def user_profile_setname():
    data = request.get_json()
    return dumps(user_profile_setname_v1(data['token'], data['name_first'], data['name_last']))

#user profile setemail
@APP.route("/user/profile/setemail/v1", methods = ['PUT'])
def user_profile_setemail():
    data = request.get_json()
    return dumps(user_profile_setemail_v1(data['token'], data['email']))

#user profile sethandle
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle_v1():
    request_data = request.get_json()
    return dumps(user_profile_sethandle(request_data['token'], request_data['handle_str']))

# users all
@APP.route("/users/all/v1", methods=['GET'])
def users_all_v0():
    token = request.args.get('token')
    return dumps(users_all_v1(token))

#user profile
@APP.route("/user/profile/v1", methods=['GET'])
def user_profile_details_v1():
    token = request.args.get('token', None)
    u_id = request.args.get('u_id', None)
    return dumps(user_profile_v1(token, int(u_id)))

############################################## AUTH ROUTES ############################################## 

#auth register
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    request_data = request.get_json()
    return dumps(auth_register_v1(request_data['email'], request_data['password'], request_data['name_first'], request_data['name_last']))

#auth login
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2():
    request_data = request.get_json()
    return dumps(auth_login_v1(request_data['email'], request_data['password']))

#auth logout
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1():
    request_data = request.get_json()
    return dumps(auth_logout(request_data['token']))


@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_password_reset_request():
    request_data = request.get_json()
    return dumps(mail.send(auth_passwordreset_request_v1(request_data['email'])))

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_password_reset_reset():
    request_data = request.get_json()
    return dumps(auth_password_reset_v1(int(request_data['reset_code']),request_data['new_password']))

############################################## DM ROUTES ############################################## 

#dm create
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1():
    request_data = request.get_json()
    return dumps(dm_create(request_data['token'], request_data['u_ids']))

#dm messages
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_v1():
    token = request.args.get('token', None)
    dm_id = request.args.get('dm_id', None)
    start = request.args.get('start', None)
    return dumps(dm_messages(token, int(dm_id), int(start)))

#dm list
@APP.route("/dm/list/v1", methods=['GET'])
def user_dm_list_v1():
    token = request.args.get('token', None)
    return dumps(dm_list_v1(token))

#dm remove
@APP.route("/dm/remove/v1", methods=['DELETE'])
def user_dm_delete_v1():
    data = request.get_json()
    token = data.get('token')
    dm_id = data.get('dm_id')
    return dumps(dm_remove_v1(token, dm_id))

#dm details
@APP.route("/dm/details/v1", methods=['GET'])
def user_dm_details_v1():
    token = request.args.get('token', None)
    dm_id = request.args.get('dm_id', None)
    return dumps(dm_details_v1(token, int(dm_id)))

#dm leave
@APP.route("/dm/leave/v1", methods=['POST'])
def user_dm_leave_v1():
    request_data = request.get_json()
    return dumps(dm_leave_v1(request_data['token'], request_data['dm_id']))

'''@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2_get():
	token, channel_id, start = request.args.get('token', None), request.args.get('channel_id', None), request.args.get('start', None)
	return dumps(channel_messages_v2(token, int(channel_id), int(start)))'''


############################################## MESSAGE ROUTES ############################################## 

#message send
@APP.route("/message/send/v1", methods=['POST'])
def message_send_v1_post():
    request_data = request.get_json()
    return dumps(message_send_v1(request_data['token'], request_data['channel_id'], request_data['message']))

#message edit
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1_put():
    request_data = request.get_json()
    return dumps(message_edit_v1(request_data['token'], request_data['message_id'], request_data['message']))

#message remove
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1_delete():
    data = request.get_json()
    token = data.get('token')
    message_id = data.get('message_id')
    return dumps(message_remove_v1(token, message_id))

#message send dm
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_v1_post():
    request_data = request.get_json()
    return dumps(message_senddm_v1(request_data['token'], request_data['dm_id'], request_data['message']))

#message sendlater
@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater_post():
    request_data = request.get_json()
    return dumps(message_sendlater_v1(request_data['token'], request_data['channel_id'], request_data['message'], request_data['time_sent']))

#message sendlater dm
@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm_post():
    request_data = request.get_json()
    return dumps(message_sendlaterdm_v1(request_data['token'], request_data['dm_id'], request_data['message'], request_data['time_sent']))


############################################## ADMIN & MISC ROUTES ############################################## 

# clear
@APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    return dumps(clear_v1())

# admin user permission change
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change_v1():
    request_data = request.get_json()
    return dumps(admin_userpermission_change(request_data['token'], request_data['u_id'], request_data['permission_id']))

# admin user remove
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    
    """
    token = request.args.get('token', None)
    u_id  = int(request.args.get('u_id', None))
    """

    payload = request.get_json()
    u_id = payload.get('u_id')
    token = payload.get('token')
    admin_user_remove_v1(token, u_id)

    return dumps({})
    
@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():
    request_data = request.get_json()
    return dumps(message_share(request_data['token'], request_data['og_message_id'], request_data['message'], request_data['channel_id'], request_data['dm_id']))

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    request_data = request.get_json()
    return dumps(message_react_v1(request_data['token'], request_data['message_id'], request_data['react_id']))

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    request_data = request.get_json()
    return dumps(message_unreact_v1(request_data['token'], request_data['message_id'], request_data['react_id']))

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    request_data = request.get_json()
    return dumps(message_pin_v1(request_data['token'], request_data['message_id']))

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    request_data = request.get_json()
    return dumps(message_unpin_v1(request_data['token'], request_data['message_id']))

@APP.route("/search/v1", methods=['GET'])
def search_v1():
    token = request.args.get('token', None)
    query_str = request.args.get('query_str', None)
    return dumps(search(token, query_str))

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto_v1():
    request_data = request.get_json()
    return dumps(user_profile_uploadphoto(request_data['token'], request_data['img_url'], request_data['x_start'], request_data['y_start'], request_data['x_end'], request_data['y_end']))

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)

# notifications_get route
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token', None)
    return dumps(notifications_get_v1(token))


############################################## STANDUP ROUTES ############################################## 
@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token', None)
    channel_id = request.args.get('channel_id', None)
    return dumps(standup_active_v1(token, int(channel_id)))

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    request_data = request.get_json()
    return dumps(standup_start_v1(request_data['token'], request_data['channel_id'], request_data['length']))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_start_post():
    request_data = request.get_json()
    return dumps(standup_send_v1(request_data['token'], request_data['channel_id'], request_data['message']))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
