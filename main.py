import socket
import select
import sys
import threading
import configparser
import json


class ChatClient:
    def __init__(self, p_host, p_port, username):
        self.host = p_host
        self.port = p_port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(2)
        self.connected = True

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
        except Exception as e:
            print(f'Verbindung fehlgeschlagen: {e}')
            sys.exit()

    def close_connection(self):
        self.connected = False

    def run(self):
        self.connect()
        input_thread = threading.Thread(target=self.send_messages)
        input_thread.daemon = True
        input_thread.start()

        while self.connected:
            try:
                ready_to_read, ready_to_write, in_error = select.select([self.client_socket], [], [], 0.5)
                if not ready_to_read:
                    continue
            except select.error as e:
                print(f"Select Error: {e}")
                break

            for sock in ready_to_read:
                try:
                    data = sock.recv(4096)
                    if not data:
                        print('\nDisconnected from chat server')
                        break
                    else:
                        msg = json.loads(data.decode())
                        sys.stdout.write(f"{msg['user_name']}: {msg['message']} ")
                        sys.stdout.flush()
                except Exception as e:
                    print(f'Fehler beim Empfangen von Daten: {e}')
                    break

        if self.client_socket:
            self.client_socket.close()
        sys.exit()

    def send_messages(self):
        sys.stdout.write(f'[{self.username}] ')
        sys.stdout.flush()
        while self.connected:
            msg = sys.stdin.readline().strip()
            if msg.lower() == "exit":
                print('Programm wird beendet...')
                self.close_connection()
                break

            if self.is_connected():
                msg = self.jsonfy(msg)
                self.client_socket.send(msg.encode())
                sys.stdout.write(f'[{self.username}] ')
                sys.stdout.flush()

    def is_connected(self):
        try:
            self.client_socket.getpeername()
            return True
        except Exception as e:
            print(f'Error while checking connection: {e}')
            return False

    def jsonfy(self, message):
        return json.dumps({"user_name": f"{self.username}", "message": message})


def read_config(filename="client.conf"):
    rc_config = configparser.ConfigParser()
    rc_config.read_file(open(filename, "r"))
    configuration = dict()
    configuration["Server"] = rc_config.get('ClientConfiguration', 'server')
    configuration["Port"] = int(rc_config.get('ClientConfiguration', 'port'))
    configuration["Username"] = rc_config.get('ClientConfiguration', 'username')
    return configuration


if __name__ == "__main__":
    config = read_config()
    host = config["Server"]
    port = config["Port"]
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    client = ChatClient(host, port, config["Username"])
    client.run()
