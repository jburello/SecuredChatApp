import socket  
import threading  
from datetime import datetime
import ssl

# Server info 
host = '127.0.0.1'  # Localhost (only local connections)
port = 65432        # Port number

# Create SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

# Create and bind the raw socket
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_socket.bind((host, port))
raw_socket.listen()

# Lists to keep track clients and nicknames
clients = []
nicknames = []


def command_list(client):
    # Send the list of connected users to the client
    user_list = ', '.join(nicknames)
    client.send(f"Connected users: {user_list}".encode('UTF-8'))

def command_help(client):
    client.send("Available commands:\n/list - List of connected users\n/help - Show this help message\n/exit - Use this command to exit the chat".encode('UTF-8'))
    
def command_exit(client):
    index = clients.index(client)
    nickname = nicknames[index]
    client.send("You have left the chat!".encode('UTF-8'))
    client.close()
    clients.remove(client)
    nicknames.remove(nickname)
    broadcast(f"{nickname} Has left the chat!")
    print(f"{nickname} has left voluntarily")

    
# Commands dictionary to map commands to functions
commands = {
    "/list": command_list,
    "/help": command_help,
    "/exit": command_exit,
    }

def handle_command(command, client):
    command = command.strip()
    if command in commands:
        commands[command](client)
    else:
        client.send(f"Error: '{command}' is not a valid command, for more info use /help.".encode('UTF-8'))


# Function to send a message to all clients
def broadcast(message):
    print(f"[DEBUG] Broadcasting message: {message}")
    for client in clients:
        try:
            # Send normal messages without command prefix
            client.send(message.encode('UTF-8'))
        except:
            # Remove failed clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} has left the chat")



# Function to handle messages from a single client
def handle(client):
    while True:
        
        try:
            # Receive message from client
            message = client.recv(1024)
            print(f"[DEBUG] Received raw message: {message}")
            #get current time for timestamps
            current_time = datetime.now()
            msg_time = current_time.strftime("%H:%M")
            
            # Send the message to all other clients
            if message.decode('UTF-8').startswith('/'): # Check if the message is a command
                # If the message is a command, handle it
                handle_command(message.decode('UTF-8'), client)
            else:
                # Otherwise, broadcast the message
                decoded_msg = message.decode('UTF-8')
                formatted_msg = f"[{msg_time}] {decoded_msg}"
                broadcast(formatted_msg)
        except:
            # If client disconnects, remove them
            index = clients.index(client)
            clients.remove(client)
            client.close()
            
            # Inform everyone the client left
            nickname = nicknames[index]
            broadcast(f"{nickname} has left the chat.".encode('UTF-8'))
            nicknames.remove(nickname)
            break

def client_thread(client, address):
    print(f"Connected with {address}")

    try:
        client.send("@@NICK".encode('UTF-8'))  # Ask for nickname
        nick_message = client.recv(1024).decode('UTF-8')

        if not nick_message.startswith("@@NICK"):
            client.send("@@ERROR Nickname cannot be empty".encode('UTF-8'))
            client.close()
            return

        nickname = nick_message[7:].strip()

        if not nickname:
            client.send("@@ERROR Nickname cannot be empty".encode('UTF-8'))
            client.close()
            return

        if len(nickname) > 20:
            client.send("@@ERROR Nickname too long (max 20 characters)".encode('UTF-8'))
            client.close()
            return

        if nickname in nicknames:
            client.send("@@ERROR Nickname already in use".encode('UTF-8'))
            client.close()
            return

        # Valid nickname
        clients.append(client)
        nicknames.append(nickname)
        client.send("@@VALID".encode('UTF-8'))
        print(f"{nickname} joined from {address}")
        broadcast(f"{nickname} joined the chat.")

        handle(client)  # Start listening for messages

    except Exception as e:
        print(f"Registration error with {address}: {str(e)}")
        client.close()

def receive():
    print(f"Server running on {host}:{port}")
    while True:
        client_raw, address = raw_socket.accept()
        try:
            client = context.wrap_socket(client_raw, server_side=True)
            thread = threading.Thread(target=client_thread, args=(client, address), daemon=True)
            thread.start()
        except ssl.SSLError as e:
            print(f"SSL handshake failed with {address}: {e}")

receive()