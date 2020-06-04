import socket, threading, tkinter, sys

HEADERLENGTH = 8
GENERAL_MSG_CODE = 1
USER_MSG_CODE = 2
ERROR_MSG_CODE = 3

QUIT_MSG = 'END_CONN'

USERNAME_LENGTH = 20
username = ''

ERR_DUPLICATE_USERNAME = '100'
ERR_NULL = '000'

ERR_MESSAGE_FG = '#d61604'

MESSAGE_BROADCAST_BG = '#05090f'

GENERAL_MSG_FG = '#00b803'

OWN_MESSAE_FG = '#e6eaf0'
OWN_USERNAME_FG = '#4085ff'

OTHER_MESSAGE_FG = '#e6eaf0'
OTHER_USERNAME_FG = '#f0ad1d'


host = input("Enter server name: ")
port = 4000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#############################################################################################################################################################
def PackMessage(message):
    print('START PACK')
    # if message == '{quit}':
        # print('END PACK')
        # return(message)
    msg_size = str(len(message)) # get length of message and convert to string
    msg_size = msg_size.ljust(HEADERLENGTH, ' ') # padd it with spaces to the left side to get it upto HEADERLENGTH characters long
    message = msg_size + message # new string is the prepped message
    print('END PACK')

    return(message)

#############################################################################################################################################################
def RetrieveMessage(sock):
    print('START RETRIEVE')
    message = dict()
    # message_length = int( sock.recv(HEADERLENGTH).decode('utf-8').strip() )
    # while True:#################################### you might need it ##############################################################
    message_header = sock.recv(HEADERLENGTH).decode('utf-8') # check if this can be done in a single line
        # if message_header != '':
            # break
    print('MESSAGE HEADER "', message_header, '"')
    message_length = int(message_header) # get the length of the message to be extracted

    message_type = sock.recv(1) # the message type - a single character long

    message_type = int(message_type.decode('utf-8').strip())

    if message_type == GENERAL_MSG_CODE: # for a general message, just message type and the message
        msg = sock.recv(message_length)
        msg = msg.decode('utf-8')
        message['type'] = GENERAL_MSG_CODE
        message['message'] = msg

    elif message_type == USER_MSG_CODE: # for user message- message type, username, message
        uname = sock.recv(USERNAME_LENGTH)
        uname = uname.decode('utf-8')

        msg = sock.recv(message_length)
        msg = msg.decode('utf-8')

        message['type'] = USER_MSG_CODE
        message['username'] = uname.strip()
        message['message'] = msg

    elif message_type == ERROR_MSG_CODE: # for error message- message type, error message
        err_msg = sock.recv(message_length)
        err_msg = err_msg.decode('utf-8')
        message['type'] = ERROR_MSG_CODE
        message['message'] = err_msg

    print('END RETRIEVE')

    return(message)


#############################################################################################################################################################
def GetMessages(sock):
    print('START GETMESSAGES')
    global username
    while True:
        try:

            while True:
                if not (username == ''): # message retrieval is not allowed to start till the username is approved by server and set
                    break

            print('START GET MESSAGES RETRIEVE')
            
            message = RetrieveMessage(sock) # get message but as a dictionary
            print('END GET MESSAGES RETRIEVE')
            
            msg_list.config(state = 'normal') # to allow messages to be added
            msg = message['message']

            if message['type'] == GENERAL_MSG_CODE: 
                msg_list.insert(tkinter.END, msg + '\n\n', 'general_message') # format for a general message

            elif message['type'] == USER_MSG_CODE: # for a user message...
                uname = message['username']
                print('UNAME:', uname, ':')
                print('USERNAME:', username, ':')

                if uname == username: # if it's from us
                    msg_list.insert(tkinter.END, uname + '\n', 'own_username')
                    msg_list.insert(tkinter.END, msg + '\n\n', 'own_message')
                else: # if it's from the others
                    msg_list.insert(tkinter.END, uname + '\n', 'other_username')
                    msg_list.insert(tkinter.END, msg + '\n\n', 'other_message')
                    


            msg_list.config(state = 'disabled') # lock the messagearea again to avoid tampering

            msg_list.yview(tkinter.END) # scroll down to the latest message


        except OSError: # error?? but what kind and what does it take to trigger it
            break
    print('END GETMESSAGES')
    

#############################################################################################################################################################
def Send(event=None):
# def send():
    
    print("SENDING STARTED")
    global my_message
    msg = my_message.strip() # get the message and remove all the leading and trailing white spaces

    if msg == '': # if it's an empty string
        return(0) # ditch
 
    my_message = '' # set the message to empty
    UpdateTextArea() # update text ares

    msg = PackMessage(msg) # prep message

    print('PACKED MESSAGE', msg) 
    client_socket.send(bytes(msg, "utf8")) # send message


    print("SENDING FINISHED")
    

# have you seen egg
#############################################################################################################################################################
def Quit(event=None):
    print("CLOSING STARTED")

    quit_msg = QUIT_MSG # set quit_msg as the QUIT_MSG
    client_socket.send(bytes(quit_msg, "utf8")) # send quit message without prepping it, essential for identifying it at the server end
    client_socket.close() #close

    # root.quit()
    root.destroy() # close window

    print("CLOSING FINISHED")

#############################################################################################################################################################
def UpdateMyMessage(event = None):
    print("UPDATING MY_MESSAGE STARTED")

    global my_message
    my_message = text_area.get("1.0",'end-1c') # get the message except for that last new line
    print("UPDATING MY_MESSAGE FINISHED")

#############################################################################################################################################################
def UpdateTextArea():
    print("UPDATING TEXT AREA STARTED")
    global my_message
    text_area.delete(1.0, tkinter.END) # clear out the text area 
    text_area.insert(tkinter.END, my_message) # set the text as that in the the my_message variable

    if my_message == '': # can be commented?? haven't checked
        pass
    print("UPDATING TEXT AREA FINISHED")

#############################################################################################################################################################
def SendUsername(event = None):
    print('START SendUsername')

    global username

    uname = username_var.get()
    print('USERNAME', uname)
    if uname == '':     # ditch if nothing was in the entry widget
        return(0)

    uname = PackMessage(uname) # prepare message
    client_socket.send(bytes(uname, "utf8"))

    err_msg = RetrieveMessage(client_socket) # recv error message from server regarding the validity of username

    if err_msg['message'] == ERR_NULL: # no error
        username_entry_error_var.set('') #set error message label to empty
        # break
    
    elif err_msg['message'] == ERR_DUPLICATE_USERNAME: # if username already exists
        username_entry_error_var.set('Username has already been taken!') # set error message
        username_entry_error_label.config(fg = ERR_MESSAGE_FG)  #set color of error message
        return(0) # ditch function
        
    #when username is validated
    username_entry.config(state = 'disabled') #disable entry widget 
    text_area.config(state = 'normal') # make message box useable
    send_button.config(state = 'normal')
    text_area.focus()

    # client_socket.send(bytes(uname, "utf8"))

    username = username_var.get() # set value of username to the username variable
    print('END SendUsername')

#############################################################################################################################################################
def LimitUsername(*args):
    uname = username_var.get()
    if len(uname) > USERNAME_LENGTH: #if uname is longer than USERNAME_LENGTH
        username_var.set(uname[:USERNAME_LENGTH]) # cut it down to the proper size

#############################################################################################################################################################
root = tkinter.Tk() #the 'root' of the GUI, the main window. Everything else inherits from this 
root.title("The Void")
# root.config(bg = 'black')

username_input_frame = tkinter.Frame(root)####################################################### the top part of the GUI where you enter the username is contained in this

username_entry_prompt_var = tkinter.StringVar() #variable associated the entry prompt
username_entry_prompt_label = tkinter.Label(username_input_frame, textvariable = username_entry_prompt_var) #label
username_entry_prompt_var.set("Enter your username") # setting the prompt message
username_entry_prompt_label.pack(padx=(20,0), pady=10, side = tkinter.LEFT) 


username_var = tkinter.StringVar() # variable associated with username
username_var.trace_variable('w', LimitUsername) #when write happens, the ListUsername function is invoked
username_var.set('') #initial value set to empty
username_entry = tkinter.Entry(username_input_frame, textvariable = username_var) # the actual entry box where they'll enter the username
username_entry.bind('<Return>', SendUsername) # pressing enter in the entry widget invokes the SendUsername function
username_entry.pack(padx=7, pady=10, side = tkinter.LEFT)

username_entry.focus() # sets focus to entry widget in the beginning


username_entry_error_var = tkinter.StringVar() # variable for the error message
username_entry_error_label = tkinter.Label(username_input_frame, textvariable = username_entry_error_var) # label for error
username_entry_error_var.set('') # no error message in the beginning

username_entry_error_label.pack(padx=5, pady=10, side = tkinter.LEFT)



username_input_frame.pack(fill = tkinter.X)######################################################


messages_frame = tkinter.Frame(root)######################################################################### # frame where the messages are printed out

scrollbar_msg_list = tkinter.Scrollbar(messages_frame)  # scrollbar for text widget
msg_list = tkinter.Text(messages_frame, height = 15, width = 80, wrap = tkinter.WORD, yscrollcommand=scrollbar_msg_list.set )# text widget where messages are printed out
scrollbar_msg_list.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
# msg_list.pack(side=tkinter.LEFT, padx = (20,0))


msg_list['bg'] = MESSAGE_BROADCAST_BG #setting background colour 
msg_list.tag_configure('own_message', justify = 'right', foreground = OWN_MESSAE_FG) #creating tag for own message
msg_list.tag_configure('own_username', justify = 'right', foreground = OWN_USERNAME_FG) # creating tag for own username

msg_list.tag_configure('other_message', justify = 'left', foreground = OTHER_MESSAGE_FG) # creating tag for other message
msg_list.tag_configure('other_username', justify = 'left', foreground = OTHER_USERNAME_FG) # creating tag for pother username

msg_list.tag_configure('general_message', justify = 'center', foreground = GENERAL_MSG_FG) # creating tag for general message


msg_list.config(state = 'disabled')

msg_list.pack()
messages_frame.pack()#########################################################################################

my_message = ''
input_frame = tkinter.Frame(root)
scrollbar_text_area = tkinter.Scrollbar(input_frame)  

text_area = tkinter.Text(input_frame, width = 75, height = 5, wrap = tkinter.WORD, yscrollcommand=scrollbar_text_area.set ) # text widget to write messages
scrollbar_text_area.pack(side=tkinter.RIGHT, fill=tkinter.Y)



text_area.config(state = 'disabled') # starts off disabled

text_area.bind('<KeyRelease>', UpdateMyMessage)

text_area.pack(side = tkinter.RIGHT)
input_frame.pack(pady = (18,0))

button_frame = tkinter.Frame(root)

quit_button = tkinter.Button(root, text = 'QUIT', command = Quit, height = 1, width = 10, bg = '#870000', fg = 'white') # button to quit
quit_button.pack(padx= (20,0), pady=13, side = tkinter.LEFT) 

send_button = tkinter.Button(root, text = 'SEND', command = Send, height = 1, width = 10, bg = '#006333', fg = 'white') # button to send message
send_button.pack(padx= (0,20), pady=13, side = tkinter.RIGHT)

send_button.config(state = 'disabled')
button_frame.pack()

root.protocol("WM_DELETE_WINDOW", Quit) # setting function to be run on closing the window




client_socket.connect((host, port))

TH = threading.Thread(target = GetMessages, args = (client_socket,))
TH.daemon = True # making it a daemon thread so that program can close even if it is still running
TH.start()


root.resizable(0, 0) # keeing window un-resizeable

tkinter.mainloop()

'''
Find the network address and the directed broadcast address of subnetted Class A IPv4 address 10.220.122.80 with a subnet mask of 255.128.0.0

network address = take the bitwise and of the respective binary conversions of ipv4add and the subnet mask


'''