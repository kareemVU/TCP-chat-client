import socket
import sys
import select

def displayServerMessage(message):
    message = message.decode("utf-8").strip()

    if (message.startswith("SEND-OK")):
        print("(Message send)")
    
    elif (message.startswith("DELIVERY")):
        message = message[9:]
        gapIndex = message.index(" ")
        message = message[:gapIndex]+":"+message[gapIndex:]
        print(message)
    
    elif (message.startswith("WHO-OK")):
        message = "Online users:"+message[6:]
        print(message)
    
    elif (message.startswith("UNKNOWN")):
        print("Message delivery failed! The user is offline.")
    
    else:
        print(message)


host = ("127.0.0.1",9999)
print("\n*** Welcome to the chat client ***\n")

''' Login Loop
Asks the user to pick the username and checks if the username is already in user or not.
If the username is already in use we ask the user for another one, until he enters a valid one.
'''
while True:
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
        clientSocket.connect(host)
    except OSError:
        print("Unreachable network. Please check your internet connection and try again.\n")
        sys.exit()

    print("Choose a username, or enter !quit to exit the program.")
    username = input("Username: ")
    if (username == "!quit"):
        clientSocket.close()
        sys.exit()

    message = ("HELLO-FROM {0}\n".format(username)).encode("utf-8")
    clientSocket.sendall(message)

    serverMessage = (clientSocket.recv(9999)).decode("utf-8")
    if (serverMessage.startswith("IN-USE")):
        clientSocket.close()
        print("\nUsername already in use, please choose another one.")

    elif (serverMessage.startswith("BUSY")):
        print("The server is busy. Please try again in few minutes.\n")
        clientSocket.close()
        sys.exit()
        
    else:
        print('\nSuccesful login.\nHello {0}!'.format(username))
        break

inputStreams = [socket.socket(),clientSocket]
serverMessage = bytes()

while True:
    
    readStreams,writeStreams,errorStreams = select.select(inputStreams,[],[])

    for inputStream in readStreams:
        if inputStream == clientSocket: 
            try:
                recievedBytes = clientSocket.recv(2)
                serverMessage = serverMessage + recievedBytes
                if(serverMessage.decode().endswith("\n")):
                    displayServerMessage(serverMessage)
                    serverMessage = bytes()     
            except TimeoutError:
                print("Unreachable network. Please check your internet connection and try again.\n")
                sys.exit()

        else: # User Input
            command = socket.socket().readline().strip()
            if (command == "!quit"):
                clientSocket.close()
                sys.exit()
            
            elif (command == "!who"):
                message = "WHO\n".encode("utf-8")
                clientSocket.sendall(message)
            
            elif (command.startswith("@")):
                command = command[1:]
                try: 
                    (user, chatMessage) = command.split(maxsplit=1)
                except ValueError:
                    print("Invalid command syntax. To send a message you have to use the following syntax: \n @<username> <message>")
                    continue
                
                message = ("SEND {0} {1}\n".format(user,chatMessage)).encode("utf-8")
                clientSocket.sendall(message)

                
                while True:
                    try:
                        recievedBytes = clientSocket.recv(2)
                        serverMessage = serverMessage + recievedBytes
                        if(serverMessage.decode().endswith("\n")):
                            displayServerMessage(serverMessage)
                            serverMessage = bytes()
                            break
                    except TimeoutError:
                        print("Unreachable network. Please check your internet connection and try again.\n")
                        sys.exit()

            
            
            else:
                print("Invalid command")