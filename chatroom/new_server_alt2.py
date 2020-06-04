# Potential To-Dos
# in client side- keep track of uname of last sent message 
# proper color scheme

import socket, threading

HEADERLENGTH = 8

GENERAL_MSG_CODE = 1
USER_MSG_CODE = 2
ERROR_MSG_CODE = 3

QUIT_MSG = 'END_CONN'

USERNAME_LENGTH = 20

ERR_DUPLICATE_USERNAME = '100'
ERR_NULL = '000'

host = socket.gethostbyname(socket.gethostname())

port = 4000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
clients = {}

# addresses = {}
print(host)
print("Server is online")
serverRunning = True

#############################################################################################################################################################
def RetrieveMessage(conn):
    print('START RETRIEVE MESSAGE')
    message_header = conn.recv(HEADERLENGTH)  # getting the first HEADERLENGTH characters
    temp = message_header.decode('utf-8').strip()
    if temp == QUIT_MSG: # if it turns out tobe a quit messages, return the appropriate values
        print('END RETRIEVE MESSAGE')

        return 1, temp

    message_length = int(temp) # if it isn't a quit message then it'd have to be the size of the message

    message = conn.recv(message_length).decode('utf8') # getting the main message

    print('END RETRIEVE MESSAGE')

    return 0, message
    # the reason 2 values are being returned is to avoid ambiguity in case the user sends the quite message as a user message or sets their username as the quit message
    # so an actual quite message would be (1, QUIT_MSG) while the one sent by the user would be (0, QUIT_MSG)


#############################################################################################################################################################
def PackMessage(message, msg_type, username = '' ):
    print('START PACK')
    msg_size = str(len(message)) # getting length of message, converting it to string
    msg_size = msg_size.ljust(HEADERLENGTH, ' ') # padding it with spaces to the left to get it up to HEADERLENGTH characters

    # constructing the message based on the message type 
    if msg_type == GENERAL_MSG_CODE: 
        msg_type = str(msg_type)
        message = msg_size + msg_type + message
        print('PACKED MESSAGE', message)

    elif msg_type == USER_MSG_CODE:
        msg_type = str(msg_type)
        uname = username.ljust(USERNAME_LENGTH, ' ')

        message = msg_size + msg_type + uname + message
        print('PACKED MESSAGE', message)

    elif msg_type == ERROR_MSG_CODE:
        msg_type = str(msg_type)
        message = msg_size + msg_type + message
        print('PACKED MESSAGE', message)

    print('END PACK')    
    return(message)

#############################################################################################################################################################
def ServiceClient(conn):  #function in thread
    username = '' # has to be kept here and not outside as global. has to bepart of thread or else only the latest username will be stored , i.e, it'll always be overwritten
    try:
        print("CHECKPOINT1")
        while True: #keeps looping till they quit or a proper username is chosen
            chk = 1
            chk_quit, temp = RetrieveMessage(conn) # getting the message from the connection along with some additional info
            if temp == QUIT_MSG and chk_quit == 1: #check the RetrieveMessage function to understand this bit properly
                # if a quit message was sent before even the username was written...
                try:
                    conn.close()
                    print("CONNECTION CLOSED")
                    return(0)
                    
                except:
                    print("POST CHECKPOINT1, COULDN'T DO SHIT")

            username = temp # if it wasn't a quit message then assign the value to username variable
            print("TEMP ASSIGNED TO USERNAME")
            for key in clients: # checking whether username has already been taken

                if clients[key] == username: # duplicate username found!
                    chk = 0 # chk is toggled for a later check
                    err_msg = ERR_DUPLICATE_USERNAME # setting the proper error message
                    err_msg = PackMessage(err_msg, ERROR_MSG_CODE) # prepping the message
                    # conn.send(bytes(err_msg, "utf8"))
                    conn.send(err_msg.encode('utf-8'))

                    break
            if chk: 
                err_msg = ERR_NULL # setting proper error message (null)
                err_msg = PackMessage(err_msg, ERROR_MSG_CODE) #prepping
                # conn.send(bytes(err_msg, "utf8"))
                conn.send(err_msg.encode('utf-8'))

                break #break out of the infinite loop once the username has been chosen


        print("CHECKPOINT2")

        
        print('USERNAME', username)
        # welcome_msg = PackMessage('Welcome to The Void, %s' % username, GENERAL_MSG_CODE)
        # conn.send(bytes(welcome_msg, "utf8")) 
        # conn.send(welcome_msg.encode('utf-8')) 
        conn.send(PackMessage('Welcome to The Void, %s' % username, GENERAL_MSG_CODE).encode('utf-8'))  # just a shortened version of the code above
                                                                                                                


        new_user_msg = "%s has joined The Void" % username
        new_user_msg = PackMessage(new_user_msg, GENERAL_MSG_CODE) 
        broadcast(new_user_msg)
        clients[conn] = username # adding new connection to the dictionary of connections
        #it's not done earlier to avoid broadcasting the new_user_msg to the new user  

        while True:

            print("CHECKPOINT3")

            chk_quit, raw_user_msg = RetrieveMessage(conn) # gets either user messages or quit messages

            print(chk_quit, raw_user_msg)
            print("CHECKPOINT4")

            if raw_user_msg == QUIT_MSG and chk_quit == 1: # conditions to be satisfied for the message to have been a quit message
                
                conn.close() 
                del clients[conn]
                print("%s has left the chat." % username)

                broadcast(PackMessage("%s has left The Void." % username, GENERAL_MSG_CODE))

                break

            else: # if it turns out to be a user message...

                print("CHECKPOINT5")

                message = PackMessage(raw_user_msg, USER_MSG_CODE, username)
                broadcast(message)
                print("CHECKPOINT6")   



                
    except:
        try:
            conn.close()
            del clients[conn]
        except:
            pass
        if username != '':
            print("%s has left The Void." % username)
            broadcast(PackMessage("%s has left the chat." % username, GENERAL_MSG_CODE))
        else:
            print('ERROR')
        
#############################################################################################################################################################
def broadcast(msg):
    msg = msg.encode('utf8')
    for client_sock in clients:
        # sock.send(bytes(msg, "utf8"))
        client_sock.send(msg)


#############################################################################################################################################################
while True:
    conn, addr = s.accept()
    print("%s:%s has connected." % addr) # printed on terminal
    # addresses[conn] = addr
    threading.Thread(target = ServiceClient, args = (conn,)).start()


