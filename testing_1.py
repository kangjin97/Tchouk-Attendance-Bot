import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint
import datetime

#Initialize token and authorize database
token = '1057289810:AAH9VmpZwd8xWOHt6K03qc5eceFNpAwqWIE'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('tchoukers.json', scope)
client = gspread.authorize(creds)

#VARIABLES
#GSHEET
loginSheet = client.open('Tchouk Attendance').worksheet("Userid")
attendanceSheet = client.open('Tchouk Attendance').worksheet("Attendance")
eventsSheet = client.open('Tchouk Attendance').worksheet("Events")
trainingSheet = client.open('Tchouk Attendance').worksheet("Training")
clubfundsSheet = client.open('Tchouk Attendance').worksheet("Club Funds")
competitionsSheet = client.open('Tchouk Attendance').worksheet("Competitions")
feedbacksheet = client.open('Tchouk Attendance').worksheet("Feedback")
creatorSheet = client.open('Tchouk Attendance').worksheet("Creator")

#GLOBALS

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

#Other Necessary Functions

#authentication

def authenticate(uid):
    registered_uid = loginSheet.col_values(1)
    uid = str(uid)
    if uid in registered_uid:
        uidcell = loginSheet.find(uid)
        return loginSheet.row_values(uidcell.row)

    return None

def protect(uid):
    registered_uid = loginSheet.col_values(1)
    uid = str(uid)
    if uid in registered_uid:
        return True
    return False

#array [day, month, weekday, weekday num]
def get_today(d=datetime.datetime.today()):
    return [d.strftime('%d'), d.strftime('%b'), d.strftime('%a'), d.strftime('%w')]

def get_attendance(tid):
    attending_dict_list = attendanceSheet.get_all_records()
    going = "Going:\n"
    not_going = "Not Going:\n"
    unsaid = "\n"
    not_going_dict = {}

    for dicts in attending_dict_list:
        if dicts["Reason"] != "":
            reason = " (" + dicts["Reason"] + ")"
        else:
            reason = ""

        if dicts['Training ID'] == int(tid) and dicts["Going"] == 1:
            going += dicts['Username'] + reason + "\n"
        elif dicts['Training ID'] == int(tid) and dicts["Going"] == 2:
            if dicts["Reason"] not in not_going_dict:
                not_going_dict[dicts["Reason"]] = []
            not_going_dict[dicts["Reason"]].append(dicts['Username'])
        else:
            unsaid += dicts["Handle"] + " "

    for key in not_going_dict.keys():
        not_going += "["+ key + "] " + ", ".join(not_going_dict[key]) + "\n"
    attendancelist = going + unsaid + "\n\n" + not_going

    return attendancelist

def get_training_id():
    training_id = int(creatorSheet.acell('B5').value)
    creatorSheet.update_acell('B5', training_id + 1)

    return training_id

def add_attendance(uid, tid):

    all_names = attendanceSheet.get_all_records()
    row_count = 2

    for dicts in all_names:
        if dicts['Training ID'] == int(tid) and dicts['Uid'] == uid:
            row_to_edit = row_count
            break
        row_count += 1

    attendanceSheet.update_cell(row_to_edit, 5, 1)
    attendanceSheet.update_cell(row_to_edit, 6, "")

def add_valid_reason(uid, tid, reason):

    all_names = attendanceSheet.get_all_records()
    row_count = 2

    for dicts in all_names:
        if dicts['Training ID'] == int(tid) and dicts['Uid'] == uid:
            row_to_edit = row_count
            break
        row_count += 1

    attendanceSheet.update_cell(row_to_edit, 5, 2)
    attendanceSheet.update_cell(row_to_edit, 6, reason)

def create_standard_training():
    day, month, weekday, weekday_num = get_today()
    standard_training_created = trainingSheet.col_values(9)
    if '1' in standard_training_created:
        return False

    if int(weekday_num) <= 1:
        next_training_day = 2
    elif int(weekday_num) <= 4:
        next_training_day = 5
    else:
        next_training_day = 0

    days_from_next_training = (next_training_day - int(weekday_num)) % 7
    training_day = datetime.datetime.today() + datetime.timedelta(days=days_from_next_training)
    training_day_info = get_today(training_day)
    reply_day = training_day - datetime.timedelta(days=1)
    reply_day_info = get_today(reply_day)

    training_venue = "SMU MPSH"
    if next_training_day != 0:
        training_time = "12PM - 3PM"
    else:
        training_time = "1PM - 4PM"

    row_value = len(trainingSheet.col_values(1))
    standard_header = "❗️Kindly RSVP by {} {} {}, 6pm❗️\n".format(reply_day_info[2], reply_day_info[0], reply_day_info[1])
    training_id = get_training_id()
    trainingSheet.insert_row(
        [training_id, standard_header, training_venue, training_time, training_day_info[3], training_day_info[2],
         training_day_info[0], training_day_info[1], 1], row_value + 1)

    fill_attendance_sheet(training_id, next_training_day)

    return training_day_info[2], training_day_info[0], training_day_info[1]

def fill_attendance_sheet(training_id, training_day):
    all_names = loginSheet.get_all_records()
    row_to_insert = len(attendanceSheet.col_values(1))
    for each_member in all_names:
        training_day = str(training_day)
        uid = each_member["ID"]
        username = each_member["Username"]
        handle = each_member["Handle"]
        going = each_member[training_day]
        reason = each_member[training_day + "reason"]
        each_column = [training_id, uid, username, handle, going, reason]
        attendanceSheet.insert_row(each_column, row_to_insert + 1)
        row_to_insert += 1




#Inline keyboards
def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Attendance", callback_data="cb_attendance"),
               InlineKeyboardButton("Events", callback_data="cb_event"),
               InlineKeyboardButton("Training", callback_data="cb_training"),
               InlineKeyboardButton("Club Funds", callback_data="cb_clubfunds"),
               InlineKeyboardButton("Competitions", callback_data="cb_competition"),
               InlineKeyboardButton("Feedback", callback_data="cb_feedback"),
               InlineKeyboardButton("Quit", callback_data="cb_quit"))
    return markup

def attendance_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Check Attendance", callback_data="cb_checkAttendance"),
               InlineKeyboardButton("Post Attendance", callback_data="cb_postAttendance"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

def reply_attendance_markup(TID, chat_id, message_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Attending", callback_data="cb_attending" + TID),
               InlineKeyboardButton("Valid Reason", callback_data="cb_validReason" + TID + "." + str(chat_id) + "." + str(message_id)),
               InlineKeyboardButton("Find Excuse", callback_data="cb_findExcuse" + TID),
               InlineKeyboardButton("Add Remark/ Update Reason", callback_data="cb_addRemark" + TID))
    return markup

def valid_reason_markup(tid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Class", callback_data="vrClass" + tid),
               InlineKeyboardButton("Fam", callback_data="vrFam" + tid),
               InlineKeyboardButton("Sick", callback_data="vrSick" + tid),
               InlineKeyboardButton("Injury", callback_data="vrInjury" + tid),
               InlineKeyboardButton("Overseas", callback_data="vrOverseas" + tid),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

#types available are post(P), check(C), delete(D)
def training_selection_markup(type):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    dict_all_trainings = trainingSheet.get_all_records()
    print (dict_all_trainings)
    for training in dict_all_trainings:
        markup.add(InlineKeyboardButton(
            "{}, {} {} {}".format(training['Weekday'], training['Day'], training['Month'], training['Time']),
            callback_data=type + "TID" + str(training['Training ID'])))
    markup.add(InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

def events_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Check Events", callback_data="cb_checkEvents"),
               InlineKeyboardButton("Create Events", callback_data="cb_createEvents"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

def training_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Create Standard Training", callback_data="cb_createStandardTraining"),
               InlineKeyboardButton("Create Custom Training", callback_data="cb_createCustomTraining"),
               InlineKeyboardButton("Delete Training", callback_data="cb_deleteTraining"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup

def feedback_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Training Feedback", callback_data="cb_trainingFeedback"),
               InlineKeyboardButton("Miscellaneous Feedback", callback_data="cb_miscFeedback"),
               InlineKeyboardButton("Back", callback_data="cb_back"))
    return markup



#FUNCTIONALITIES

# handle the "/login" command
@bot.message_handler(commands=['login'])
def command_login(m):
    uid = m.from_user.id
    cid = m.chat.id

    #Authenticate Password from Database & Determine Status
    normal_password = creatorSheet.acell('B2').value
    exco_password = creatorSheet.acell('B3').value

    if m.text[7:] == normal_password:
        status = 1
    elif m.text[7:] == exco_password:
        status = 2
    else:
        bot.send_message(cid, "Invalid Password!")
        return None

    #If not registered before, add user into database
    if not authenticate(uid):  # if user hasn't used the "/start" command yet:
        row_value = len(loginSheet.col_values(1))  # Target Row
        handle = "@" + m.from_user.username
        loginSheet.insert_row([uid, m.from_user.first_name, status, handle], row_value + 1)
        bot.send_message(cid, "User Authenticated, Welcome {}!".format(authenticate(uid)[1]))

    #If changing status, Display change
    elif status != int(authenticate(uid)[2]):
        uidcell = loginSheet.find(str(uid))
        loginSheet.update_cell(uidcell.row, 3, status)
        if status == 1:
            position = "Member"
        elif status == 2:
            position = "Exco"
        bot.send_message(cid, "Member status updated: " + position)

    #If already in database, Tell member to GTFO!
    else:
        bot.send_message(cid, "You are already registered in our database, " + authenticate(cid)[1] + " stop bugging me!")

# handle the "/menu" command
@bot.message_handler(commands=['menu'])
def command_menu(m):
    cid = m.from_user.id
    # Protect Function
    if not protect(cid):
        return None
    bot.send_message(m.chat.id, "Hello, Tchoukie! How can I help you today?", reply_markup=menu_markup())

#FeedBack

feedback_dict = {}

class Feedback:
    def __init__(self, feedback):
        self.feedback = feedback
        self.receiver_id = None
        self.receiver = None

#handle level 4 callback selections
@bot.callback_query_handler(func=lambda call: call.data.startswith("vr"))
def callback_query(call):
    print(call.message)
    user_id = call.from_user.id
    call.data = call.data.split(".")
    p_chat_id = int(call.data[1])
    p_message_id = int(call.data[2])
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    #valid reason handler ATTENDANCE
    if call.data[0].startswith("vrClass"):
        bot.answer_callback_query(call.id)
        selected_cell = trainingSheet.find(call.data[0][7:])
        training_details = trainingSheet.row_values(selected_cell.row)
        add_valid_reason(user_id, training_details[0], "Class")
        bot.send_message(chat_id, "You have updated your attendance")
        bot.edit_message_text(
            text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                       training_details[2],
                                                                                       training_details[3],
                                                                                       training_details[5],
                                                                                       training_details[6],
                                                                                       training_details[7],
                                                                                       training_details[0])
                 + get_attendance(training_details[0]),
            chat_id=p_chat_id,
            message_id=p_message_id, reply_markup=reply_attendance_markup(str(training_details[0]), p_chat_id, p_message_id))
    elif call.data[0].startswith("vrFam"):
        bot.answer_callback_query(call.id)
        selected_cell = trainingSheet.find(call.data[0][5:])
        training_details = trainingSheet.row_values(selected_cell.row)
        add_valid_reason(user_id, training_details[0], "Fam")
        bot.send_message(chat_id, "You have updated your attendance")
        bot.edit_message_text(
            text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                       training_details[2],
                                                                                       training_details[3],
                                                                                       training_details[5],
                                                                                       training_details[6],
                                                                                       training_details[7],
                                                                                       training_details[0])
                 + get_attendance(training_details[0]),
            chat_id=p_chat_id,
            message_id=p_message_id,
            reply_markup=reply_attendance_markup(str(training_details[0]), p_chat_id, p_message_id))

    elif call.data[0].startswith("vrSick"):
        bot.answer_callback_query(call.id)
        selected_cell = trainingSheet.find(call.data[0][6:])
        training_details = trainingSheet.row_values(selected_cell.row)
        add_valid_reason(user_id, training_details[0], "Sick")
        bot.send_message(chat_id, "You have updated your attendance")
        bot.edit_message_text(
            text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                       training_details[2],
                                                                                       training_details[3],
                                                                                       training_details[5],
                                                                                       training_details[6],
                                                                                       training_details[7],
                                                                                       training_details[0])
                 + get_attendance(training_details[0]),
            chat_id=p_chat_id,
            message_id=p_message_id,
            reply_markup=reply_attendance_markup(str(training_details[0]), p_chat_id, p_message_id))

    elif call.data[0].startswith("vrInjury"):
        bot.answer_callback_query(call.id)
        selected_cell = trainingSheet.find(call.data[0][8:])
        training_details = trainingSheet.row_values(selected_cell.row)
        add_valid_reason(user_id, training_details[0], "Injury")
        bot.send_message(chat_id, "You have updated your attendance")
        bot.edit_message_text(
            text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                       training_details[2],
                                                                                       training_details[3],
                                                                                       training_details[5],
                                                                                       training_details[6],
                                                                                       training_details[7],
                                                                                       training_details[0])
                 + get_attendance(training_details[0]),
            chat_id=p_chat_id,
            message_id=p_message_id,
            reply_markup=reply_attendance_markup(str(training_details[0]), p_chat_id, p_message_id))

    elif call.data[0].startswith("vrOverseas"):
        bot.answer_callback_query(call.id)
        selected_cell = trainingSheet.find(call.data[0][10:])
        training_details = trainingSheet.row_values(selected_cell.row)
        add_valid_reason(user_id, training_details[0], "Overseas")
        bot.send_message(chat_id, "You have updated your attendance")
        bot.edit_message_text(
            text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                       training_details[2],
                                                                                       training_details[3],
                                                                                       training_details[5],
                                                                                       training_details[6],
                                                                                       training_details[7],
                                                                                       training_details[0])
                 + get_attendance(training_details[0]),
            chat_id=p_chat_id,
            message_id=p_message_id,
            reply_markup=reply_attendance_markup(str(training_details[0]), p_chat_id, p_message_id))

#handle all other callback selections
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)
    print(call.message)
    user_id = call.from_user.id
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
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Which part of Events do you need assistance with?", chat_id=chat_id,
                              message_id=message_id, reply_markup=training_markup())
    elif call.data == "cb_competition":
        bot.answer_callback_query(call.id, "Please select competition")
    elif call.data == "cb_clubfunds":
        bot.answer_callback_query(call.id, "Redirecting you to the payment page")
    elif call.data == "cb_feedback":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Your feedback will greatly improve our community!", chat_id=chat_id,
                              message_id=message_id, reply_markup=feedback_markup())
    elif call.data == "cb_quit":
        bot.answer_callback_query(call.id)
        bot.delete_message(chat_id, message_id)

    #level 2 abstraction
    elif call.data == "cb_back":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    #ATTENDANCE LAYER 2
    elif call.data == "cb_checkAttendance":
        bot.answer_callback_query(call.id, "Retrieving Attendance")
        bot.edit_message_text(text="Which training attendance would you like to check?", chat_id=chat_id,
                              message_id=message_id, reply_markup=training_selection_markup('C'))
    elif call.data == "cb_postAttendance":
        bot.answer_callback_query(call.id, "Select training to post")
        #add authorization here
        bot.edit_message_text(text="Which training attendance would you like to post?", chat_id=chat_id,
                              message_id=message_id, reply_markup=training_selection_markup('P'))

    # ATTENDANCE LAYER 3
    #POST ATTENDANCE
    elif call.data.startswith('PTID'):
        bot.answer_callback_query(call.id, "posting attendance")
        selected_cell = trainingSheet.find(call.data[4:])
        training_details = trainingSheet.row_values(selected_cell.row)
        bot.send_message(chat_id, "{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                                   training_details[2],
                                                                                                   training_details[3],
                                                                                                   training_details[5],
                                                                                                   training_details[6],
                                                                                                   training_details[7],
                                                                                                   training_details[0])
                         + get_attendance(training_details[0]),
                         reply_markup=reply_attendance_markup(str(training_details[0]),chat_id ,message_id))
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    #CHECK ATTENDANCE
    elif call.data.startswith('CTID'):
        bot.answer_callback_query(call.id, "checking attendance")
        selected_cell = trainingSheet.find(call.data[4:])
        training_details = trainingSheet.row_values(selected_cell.row)
        bot.send_message(chat_id, "{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                                   training_details[2],
                                                                                                   training_details[3],
                                                                                                   training_details[5],
                                                                                                   training_details[6],
                                                                                                   training_details[7],
                                                                                                   training_details[0])
                         + get_attendance(training_details[0]))
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    #UPDATE ATTENDANCE
    elif call.data.startswith('cb_attending'):
        training_code = call.data[12:]
        bot.answer_callback_query(call.id, "You are attending training #" + training_code)
        add_attendance(user_id, training_code)
        selected_cell = trainingSheet.find(training_code)
        training_details = trainingSheet.row_values(selected_cell.row)
        bot.edit_message_text(text="{} Venue: {} \n Time: {} \n Date: {}, {} {} \n Code: {} \n\n".format(training_details[1],
                                                                                                    training_details[2],
                                                                                                    training_details[3],
                                                                                                    training_details[5],
                                                                                                    training_details[6],
                                                                                                    training_details[7],
                                                                                                    training_details[0])
                              +get_attendance(training_details[0]),
                              chat_id=chat_id,
                              message_id=message_id, reply_markup=reply_attendance_markup(str(training_details[0]), chat_id, message_id))

    elif call.data.startswith('cb_validReason'):
        training_code = call.data[14:]
        bot.answer_callback_query(call.id, "I have sent you a PM! Let me know your reason")
        bot.send_message(user_id,
                         text="Select valid reason, if it has not been stated here then you are probably looking for an excuse... GOOD FOR YOU",
                         reply_markup=valid_reason_markup(str(training_code)))

        # bot.edit_message_text(
        #     text="Select valid reason, if it has not been stated here then you are probably looking for an excuse... GOOD FOR YOU",
        #     chat_id=chat_id,
        #     message_id=message_id, reply_markup=valid_reason_markup(str(training_code)))



    #EVENTS
    elif call.data == "cb_createEvents":
        bot.answer_callback_query(call.id, "This Feature has not been implemented")
    elif call.data == "cb_checkEvents":
        bot.answer_callback_query(call.id, "This Feature has not been implemented")

    #TRAINING
    elif call.data == "cb_createStandardTraining":
        bot.answer_callback_query(call.id, "Creating training...")
        status = create_standard_training()
        if status:
            bot.send_message(chat_id, "Training created on {}, {} {}. Remember to send out attendance as well!".format(status[0], status[1], status[2]))
        else:
            bot.send_message(chat_id, "The next standard training has already been created. Remember to send out attendance!")
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    elif call.data == "cb_createCustomTraining":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Select Training", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
    elif call.data == "cb_checkEvents":
        bot.answer_callback_query(call.id, "This Feature has not been implemented")

    #FEEDBACK
    elif call.data == "cb_trainingFeedback":
        bot.answer_callback_query(call.id)
        print (chat_id)
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
        bot.send_message(chat_id, text="Please tell me your feedback, rest assured this will be 101% anonymous!")
    elif call.data == "cb_miscFeedback":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Hello, Tchoukie! How can I help you today?", chat_id=chat_id,
                              message_id=message_id, reply_markup=menu_markup())
        bot.send_message(chat_id, "Please tell me your feedback, rest assured this will be 101% anonymous!")


# def step_function():
#     bot.register_next_step_handler(msg, process_first_step)
#
# def process_first_step(message):
#     try:
#         chat_id = message.chat.id
#         name = message.text
#         user = User(name)
#         user_dict[chat_id] = user
#         msg = bot.reply_to(message, 'How old are you?')
#         bot.register_next_step_handler(msg, process_age_step)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')
#
#
# def process_name_step(message):
#     try:
#         chat_id = message.chat.id
#         name = message.text
#         user = User(name)
#         user_dict[chat_id] = user
#         msg = bot.reply_to(message, 'How old are you?')
#         bot.register_next_step_handler(msg, process_age_step)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')
#
#
# def process_age_step(message):
#     try:
#         chat_id = message.chat.id
#         age = message.text
#         if not age.isdigit():
#             msg = bot.reply_to(message, 'Age should be a number. How old are you?')
#             bot.register_next_step_handler(msg, process_age_step)
#             return
#         user = user_dict[chat_id]
#         user.age = age
#         markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#         markup.add('Male', 'Female')
#         msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
#         bot.register_next_step_handler(msg, process_sex_step)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')
#
#
# def process_sex_step(message):
#     try:
#         chat_id = message.chat.id
#         sex = message.text
#         user = user_dict[chat_id]
#         if (sex == u'Male') or (sex == u'Female'):
#             user.sex = sex
#         else:
#             raise Exception()
#         bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')


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
