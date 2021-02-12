#################################################################################
####                               Pull fingur                               ####
####  https://github.com/reddh4wk/crypto-alert-bot/edit/main/gasbot_v1.2.py  ####
#################################################################################
SPEED=["fastest", "fast", "average"]
SPAM_LIMITER_IN_SECONDS=600 #use an integer number
TOKEN = 'YOUR_TELEGRAM_API_KEY'
INSTANCES=[]
#################################################################################

# TO EDUCATE JSONs
import requests
from requests.exceptions import HTTPError
import json
# TO MESS WITH TIME
import time
# TO DO LOVE WITH TELEGRAM
import telepot

def get_gasprice():
    pullerino="https://ethgasstation.info/api/ethgasAPI.json?"
    try:
        response = requests.get(pullerino)
        response.raise_for_status()
        jsonResponse = response.json()
        for key,value in jsonResponse.items():
            if key == "fast":
                fast=value
            elif key == "fastest":
                fastest=value
            elif key == "average":
                average=value
                break
        return [fastest, fast, average]
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def price_overview():
    fastest, fast, average=get_gasprice()
    overview="Fastest: " + str(fastest/10) + " Gwei\nFast: " + str(fast/10) + " Gwei\nAverage: " + str(average/10) + " Gwei"
    return overview

def print_gasprice(price, speed_index, trend):
    global SPEED
    if trend:
        return("Price is going down! "+SPEED[speed_index].capitalize()+": "+str(price[speed_index]/10))
    else:
        return("Price is going up! "+SPEED[speed_index].capitalize()+": "+str(price[speed_index]/10))

def update_in_file(line_to_update_begin, line_updated):
    global INSTANCES
    with open(__file__, 'r') as f:
        lines = f.read().split('\n')
        nline=-1
        for ln in lines:
            nline=nline+1
            if ln.startswith(line_to_update_begin):
                break
        new_file = '\n'.join(lines[:nline] + [line_updated] + lines[(nline+1):])

    with open(__file__, 'w') as f:
        f.write(new_file)

def update_instances_in_file():
    global INSTANCES
    update_in_file("INSTANCES=[", 'INSTANCES=' + str(INSTANCES))

def is_among_instances(sender, chat, speed=None):
    global INSTANCES
    for instance in INSTANCES:
        if speed != None:
            if instance[0] == sender and instance[1] == chat and instance[3] == speed:
                virdict=True
                break
            else:
                virdict=False
        else:
            if instance[0] != sender and instance[1] != chat:
                virdict=False
            else:
                virdict=True
                break
    if INSTANCES:
        return virdict
    else:
        return False

def add_instance(sender, chat, price, speed):
    global INSTANCES
    INSTANCES.append((sender, chat, price, speed))
    update_instances_in_file()

def set_price_treshold(sender, chat, price, speed):
    global INSTANCES
    remove_instance(sender, chat, speed)
    add_instance(sender, chat, price, speed)

def remove_instance(sender, chat=None, speed=None):
    global INSTANCES
    temp_instances=[]
    if chat != None and speed != None:
        for instance in INSTANCES:
            if instance[0] != sender and instance[1] != chat and instance[3] != speed:
                temp_instances.append(instance)
    elif chat == None and speed != None:
        for instance in INSTANCES:
            if instance[0] != sender and instance[4] != speed:
                temp_instances.append(instance)
    elif chat != None and speed == None:
        for instance in INSTANCES:
            if instance[0] != sender and instance[1] != chat:
                temp_instances.append(instance)
    else:
        for instance in INSTANCES:
            if instance[0] != sender:
                temp_instances.append(instance)
    INSTANCES=temp_instances
    update_instances_in_file()

def list_current_chat(sender, chat):
    global INSTANCES
    global SPEED
    output=""
    for instance in INSTANCES:
        if instance[0] == sender and instance[1] == chat:
            output=output+"\n- "+SPEED[instance[3]].capitalize()+": "+str(instance[2])
    if output:
        return(output)
    else:
        return False

def list_all_chat(sender):
    return("I am sick of implementing shit you sandnigger")

def on_chat_message(msg):
    global SPEED
    msg_not_float='The threshold you tried to set is invalid. You need to use an integer or a dot-separated real number. Negative numbers are allowed even if it does not make much sense'
    msg_not_speed='The speed type you tried to set is invalid. Valid types are "fastest" "fast" and "average"'
    msg_price_updated='The threshold for this alert has been updated'
    msg_registration_successful='This alert has been registered in my broadcast.'
    msg_deletion_succesful='The alerts you selected have been removed from my broadcast.'
    msg_list_current_chat='The following is a list of all the alerts you set up in this chat:'
    msg_list_all_chat='The following is a list of all the alerts you set up with this bot across the chats:'
    msg_list_empty='There is no alert registered for this account on this chat.'
    msg_wrong_parameters_n='The number of parameters you used for this function is different from what I was expectring. Please check the /help command.'
    #msg_deletion_all_successful='You have been removed from my broadcast in all the chats.' #deprecated
    msg_instance_not_found='I am sorry, but you were not found in my broadcast. If you think this is an error, please contact the administrator.'
    msg_contact_admin='To get help, please send this message to the administrator.'
    msg_error_upd_threshold='I was not able to update your threshold because of the following error:'
    msg_error_add_broadcast='I was not able to add you to my broadcast because of the following error:'
    msg_error_rem_broadcast='I was not able to remove you from my broadcast because of the following error:'
    msg_help="""
List of the commands:
/help: Display this message
/set: Allow a user to register and define its threshold on this chat. The command must be in a format similar to: /set 100|100.000 fastest|fast|average
/stop: Allow a user to stop the broadcast on the current chat. If used appending the speed parameter, it only stops the alerts for the selected speed on the current chat (e.g. /delist fast)
/stopall: Allow a user to stop the broadcast on all the chats for all the alerts. If used appending the speed parameter, it only stops the alerts for the selected speed on all chats (e.g. /delistall fast)
/list: Allow to list all the alerts set up in the current chat by the user.
/price: Allow a user to get information about the gas price immediatly through the chat.

Secret commands: Only awakened beings know about such commands.

Thanks to https://ethgasstation.info/ for providing this data.
"""
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        content = msg['text'].split(" ")
        if msg['text'].startswith("/set"):
            if len(content) == 3:
                try:
                    float(content[2])
                    isfloat=True
                except Exception:
                    isfloat=False
                if isfloat:
                    if content[1] in SPEED:
                        if is_among_instances(msg['from']['id'], msg['chat']['id'], SPEED.index(content[1])):
                            try:
                                set_price_treshold(msg['from']['id'], msg['chat']['id'], float(content[2]), SPEED.index(content[1]))
                                bot.sendMessage(chat_id, msg_price_updated)
                            except Exception as err:
                                bot.sendMessage(chat_id, msg_error_upd_threshold+f'\n- {err}\n'+msg_contact_admin)
                        else:
                            try:
                                add_instance(msg['from']['id'], msg['chat']['id'], float(content[2]), SPEED.index(content[1]))
                                bot.sendMessage(chat_id, msg_registration_successful)
                            except Exception as err:
                                bot.sendMessage(chat_id, msg_error_add_broadcast+f'\n- {err}\n'+msg_contact_admin)
                    else:
                        bot.sendMessage(chat_id, msg_not_speed)
                else:
                    bot.sendMessage(chat_id, msg_not_float)
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/stop"):
            if len(content) <= 2:
                if is_among_instances(msg['from']['id'], msg['chat']['id']):
                    try:
                        if len(content) == 1:
                            remove_instance(msg['from']['id'], msg['chat']['id'])
                        elif len(content) == 2:
                            remove_instance(msg['from']['id'], msg['chat']['id'], SPEED.index(content[1]))
                        bot.sendMessage(chat_id, msg_deletion_succesful)
                    except Exception as err:
                        bot.sendMessage(chat_id, msg_error_rem_broadcast+f'\n- {err}\n'+msg_contact_admin)
                else:
                    bot.sendMessage(chat_id, msg_instance_not_found)
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/stopall"):
            if len(content) <= 2:
                if is_among_instances(msg['from']['id'], msg['chat']['id']):
                    try:
                        if len(content) == 1:
                            remove_instance(msg['from']['id'])
                        elif len(content) == 2:
                            remove_instance(msg['from']['id'], SPEED.index(content[1]))
                        bot.sendMessage(chat_id, msg_deletion_succesful)
                    except Exception as err:
                        bot.sendMessage(chat_id, msg_error_rem_broadcast+f'\n- {err}\n'+msg_contact_admin)
                else:
                    bot.sendMessage(chat_id, msg_instance_not_found)
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/list"):
            if len(content) == 1:
                list_not_empty=list_current_chat(msg['from']['id'], msg['chat']['id'])
                if list_not_empty:
                    bot.sendMessage(chat_id, msg_list_current_chat + list_current_chat(msg['from']['id'], msg['chat']['id']))
                else:
                    bot.sendMessage(chat_id, msg_list_empty)
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/listall"):
            if len(content) == 1:
                bot.sendMessage(chat_id, list_all_chat(msg['from']['id']))
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/help"):
            if len(content) == 1:
                bot.sendMessage(chat_id, msg_help)
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'].startswith("/price"):
            if len(content) == 1:
                bot.sendMessage(chat_id, price_overview())
            else:
                bot.sendMessage(chat_id, msg_wrong_parameters_n)
        elif msg['text'] == "/penis":
            bot.sendMessage(chat_id, 'Eat it')
        elif msg['text'] == "/goodboi":
            bot.sendMessage(chat_id, 'Thanks niggur')
        elif msg['text'].startswith("/"):
            bot.sendMessage(chat_id, 'The command '+content[0]+' is not recognized as a valid command. See /help for help.')

def broadcast(msg):
    global INSTANCES
    for instance in INSTANCES:
        bot.sendMessage(instance[1], msg)

bot = telepot.Bot(TOKEN)
bot.message_loop(on_chat_message)

print('Listening ...')

oldprice=get_gasprice()

while True:
    newprice = get_gasprice()
    for instance in INSTANCES:
        if newprice[instance[3]] < instance[2]*10 and oldprice[instance[3]] > instance[2]*10:
            bot.sendMessage(instance[1], print_gasprice(newprice, instance[3], True))
        if newprice[instance[3]] > instance[2]*10 and oldprice[instance[3]] < instance[2]*10:
            bot.sendMessage(instance[1], print_gasprice(newprice, instance[3], False))
        oldprice=newprice
    time.sleep(600)
