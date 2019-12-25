import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint

#Initialize token and authorize database
token = '1057289810:AAH9VmpZwd8xWOHt6K03qc5eceFNpAwqWIE'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('tchoukers.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Tchouk Attendence').sheet1

def get_attendance():
    attendancecolumn = sheet.col_values(1)
    attendancelist = ""

    for name in attendancecolumn[1:]:
        attendancelist += name + "\n"

    return attendancelist


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(token)
bot.set_update_listener(listener)  # register listener

#Inline keyboards
def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Attendance", callback_data="cb_attendance"),
               InlineKeyboardButton("Events", callback_data="cb_event"),
               InlineKeyboardButton("Training", callback_data="cb_training"),
               InlineKeyboardButton("Club Funds", callback_data="cb_clubfunds"),
               InlineKeyboardButton("Competitions", callback_data="cb_competition"))
    return markup

def attendance_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Check Attendance", callback_data="cb_checkAttendance"),
               InlineKeyboardButton("Post Attendance", callback_data="cb_postAttendance"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

def events_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Check Events", callback_data="cb_checkEvents"),
               InlineKeyboardButton("Create Events", callback_data="cb_createEvents"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

# handle the "/menu" command
@bot.message_handler(commands=['menu'])
def command_menu(m):
    cid = m.chat.id
    bot.send_message(cid, "Hello, Tchoukie! How can I help you today?", reply_markup=menu_markup())

#handle all callback selections
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    #level 1 abstraction
    if call.data == "cb_attendance":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Which part of Attendance do you need assistance with?", chat_id=chat_id,
                              message_id=message_id, reply_markup=attendance_markup())
    elif call.data == "cb_event":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Which part of Events do you need assistance with?", chat_id=chat_id,
                              message_id=message_id, reply_markup=events_markup())
    elif call.data == "cb_training":
        bot.answer_callback_query(call.id, "Please select training")
    elif call.data == "cb_competition":
        bot.answer_callback_query(call.id, "Please select competition")
    elif call.data == "cb_clubfunds":
        bot.answer_callback_query(call.id, "Redirecting you to the payment page")

    #level 2 abstraction
    elif call.data == "cb_back":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    #ATTENDANCE
    elif call.data == "cb_checkAttendance":
        bot.answer_callback_query(call.id, "Displaying Attendance")
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
        bot.send_message(chat_id, get_attendance())
    elif call.data == "cb_postAttendance":
        bot.answer_callback_query(call.id)
        #add authorization here
        bot.edit_message_text(text="Welcome Captain", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
        bot.send_message(chat_id, get_attendance())

    #EVENTS
    elif call.data == "cb_createEvents":
        bot.answer_callback_query(call.id, "This Feature has not been implemented")
    elif call.data == "cb_checkEvents":
        bot.answer_callback_query(call.id, "This Feature has not been implemented")





bot.polling(none_stop=True)

# def gen_markup():
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 2
#     markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
#                                InlineKeyboardButton("No", callback_data="cb_no"))
#     return markup
#
# @bot.callback_query_handler(func=lambda call: True)
# def callback_query(call):
#     if call.data == "cb_yes":
#         bot.answer_callback_query(call.id, "Answer is Yes")
#     elif call.data == "cb_no":
#         bot.answer_callback_query(call.id, "Answer is No")
#
# @bot.message_handler(func=lambda message: True)
# def message_handler(message):
#     bot.send_message(message.chat.id, "Yes/no?", reply_markup=gen_markup())
#
# bot.polling(none_stop=True)

# """
# This is a detailed example using almost every command of the API
# """
#
# import time
#
# import telebot
# from telebot import types
#
# TOKEN = '<token_string>'
#
# knownUsers = []  # todo: save these in a file,
# userStep = {}  # so they won't reset every time the bot restarts
#
# commands = {  # command description used in the "help" command
#     'start'       : 'Get used to the bot',
#     'help'        : 'Gives you information about the available commands',
#     'sendLongText': 'A test using the \'send_chat_action\' command',
#     'getImage'    : 'A test using multi-stage messages, custom keyboard, and media sending'
# }
#
# imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
# imageSelect.add('cock', 'pussy')
#
# hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard
#
#
# # error handling if user isn't known yet
# # (obsolete once known users are saved to file, because all users
# #   had to use the /start command and are therefore known to the bot)
# def get_user_step(uid):
#     if uid in userStep:
#         return userStep[uid]
#     else:
#         knownUsers.append(uid)
#         userStep[uid] = 0
#         print("New user detected, who hasn't used \"/start\" yet")
#         return 0
#
#
# # only used for console output now
# def listener(messages):
#     """
#     When new messages arrive TeleBot will call this function.
#     """
#     for m in messages:
#         if m.content_type == 'text':
#             # print the sent message to the console
#             print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
#
#
# bot = telebot.TeleBot(TOKEN)
# bot.set_update_listener(listener)  # register listener
#
#
# # handle the "/start" command
# @bot.message_handler(commands=['start'])
# def command_start(m):
#     cid = m.chat.id
#     if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
#         knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
#         userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
#         bot.send_message(cid, "Hello, stranger, let me scan you...")
#         bot.send_message(cid, "Scanning complete, I know you now")
#         command_help(m)  # show the new user the help page
#     else:
#         bot.send_message(cid, "I already know you, no need for me to scan you again!")
#
#
# # help page
# @bot.message_handler(commands=['help'])
# def command_help(m):
#     cid = m.chat.id
#     help_text = "The following commands are available: \n"
#     for key in commands:  # generate help text out of the commands dictionary defined at the top
#         help_text += "/" + key + ": "
#         help_text += commands[key] + "\n"
#     bot.send_message(cid, help_text)  # send the generated help page
#
#
# # chat_action example (not a good one...)
# @bot.message_handler(commands=['sendLongText'])
# def command_long_text(m):
#     cid = m.chat.id
#     bot.send_message(cid, "If you think so...")
#     bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
#     time.sleep(3)
#     bot.send_message(cid, ".")
#
#
# # user can chose an image (multi-stage command example)
# @bot.message_handler(commands=['getImage'])
# def command_image(m):
#     cid = m.chat.id
#     bot.send_message(cid, "Please choose your image now", reply_markup=imageSelect)  # show the keyboard
#     userStep[cid] = 1  # set the user to the next step (expecting a reply in the listener now)
#
#
# # if the user has issued the "/getImage" command, process the answer
# @bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
# def msg_image_select(m):
#     cid = m.chat.id
#     text = m.text
#
#     # for some reason the 'upload_photo' status isn't quite working (doesn't show at all)
#     bot.send_chat_action(cid, 'typing')
#
#     if text == "cock":  # send the appropriate image based on the reply to the "/getImage" command
#         bot.send_photo(cid, open('rooster.jpg', 'rb'),
#                        reply_markup=hideBoard)  # send file and hide keyboard, after image is sent
#         userStep[cid] = 0  # reset the users step back to 0
#     elif text == "pussy":
#         bot.send_photo(cid, open('kitten.jpg', 'rb'), reply_markup=hideBoard)
#         userStep[cid] = 0
#     else:
#         bot.send_message(cid, "Don't type bullsh*t, if I give you a predefined keyboard!")
#         bot.send_message(cid, "Please try again")
#
#
# # filter on a specific message
# @bot.message_handler(func=lambda message: message.text == "hi")
# def command_text_hi(m):
#     bot.send_message(m.chat.id, "I love you too!")
#
#
# # default handler for every other text
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def command_default(m):
#     # this is the standard reply to a normal message
#     bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")
#
# # Handle '/start' and '/help'
# @bot.message_handler(commands=['help', 'start'])
# def send_welcome(message):
#     bot.reply_to(message, """\
# Hi there, I am EchoBot.
# I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
# """)
#
#
# # Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)
