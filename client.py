import socket   
import threading
from colorama import init, Fore, Style
import ssl

init()

nickname = ""

#SSL context with certificate verification
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.check_hostname = False  # Set to True if using real domain name
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations('server_cert.pem')  # server's cert copied locally

# Connect the SSL socket
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_socket = context.wrap_socket(raw_socket, server_hostname='localhost')  # Adjust later if using real domain
ssl_socket.connect(('127.0.0.1', 65432))  # Connect to the server

def receive():
    global nickname
    while True:
        try:
            message = ssl_socket.recv(1024).decode('UTF-8')

            if message.startswith("@@"):
                if message == "@@NICK" and not nickname:
                    while True:
                        nickname_input = input("Choose your nickname: ").strip()
                        if not nickname_input:
                            print(Fore.RED + "Nickname cannot be empty!" + Style.RESET_ALL)
                            continue
                        if len(nickname_input) > 20:
                            print(Fore.RED + "Nickname too long (max 20 characters)!" + Style.RESET_ALL)
                            continue

                        ssl_socket.send(f"@@NICK {nickname_input}".encode('UTF-8'))
                        response = ssl_socket.recv(1024).decode('UTF-8')

                        if response.startswith("@@VALID"):
                            nickname = nickname_input
                            print(f"Welcome, {nickname}! Start chatting.")
                            break
                        else:
                            print(Fore.RED + response.replace("@@ERROR ", "") + Style.RESET_ALL)
                continue

            if message.startswith("@@ERROR"):
                print(Fore.RED + message.replace("@@ERROR ", "") + Style.RESET_ALL)
            elif message.startswith("@@"):
                print(Fore.GREEN + message + Style.RESET_ALL)
            else:
                print(Fore.CYAN + message + Style.RESET_ALL)

        except Exception as e:
            print(f"Error: {str(e)}")
            ssl_socket.close()
            break

def write():
    while True:
        try:
            if not nickname:
                continue
            user_input = input()
            if user_input.strip() == "":
                continue
            if user_input.startswith('/'):
                ssl_socket.send(user_input.encode('UTF-8'))
            else:
                message = f"{nickname}: {user_input}"
                ssl_socket.send(message.encode('UTF-8'))
                print(Fore.YELLOW + f"You: {user_input}" + Style.RESET_ALL)

            if user_input == '/exit':
                print("Exiting chat...")
                ssl_socket.close()
                break
        except:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
