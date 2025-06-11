# SecureChatApp

SecureChatApp is a Python-based multi-client chat application that prioritizes security by using SSL/TLS encryption for all communications. It supports multiple clients connecting concurrently to a server that manages encrypted messaging, nickname registration, and useful chat commands.

---

## Features

- **SSL/TLS Encryption:** Ensures all messages between clients and server are securely transmitted using SSL sockets.
- **Multithreaded Server:** Handles multiple clients concurrently with independent threads for each connection.
- **Nickname Management:** Users must register a unique nickname before chatting.
- **User Commands:** Supports commands such as `/list` (show connected users), `/help` (list commands), and `/exit` (leave chat).
- **Message Timestamping:** All messages are broadcast with timestamps for clear conversation context.
- **Input Validation:** Prevents empty or duplicate nicknames and enforces nickname length limits.

---

## Getting Started

### Prerequisites

- Python 3.x
- `colorama` library for colored terminal output (`pip install colorama`)

### SSL Certificates

Before running the server and client, you need to generate SSL certificates:

```bash
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
openssl x509 -in cert.pem -out server_cert.pem -outform PEM
