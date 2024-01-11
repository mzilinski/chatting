import socket
import select
import sys

# Eine Klasse, die einen Chat-Server definiert
class ChatServer:
    def __init__(self, port):
        self.host = ''
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.socket_list = [self.server_socket]
        self.clients = {}

    def broadcast(self, message, source_socket):
        for socket in self.socket_list:
            # Nachricht nicht an den Server und den Client, der die Nachricht gesendet hat, senden
            if socket != self.server_socket and socket != source_socket:
                try:
                    socket.send(message.encode())
                except Exception as e:
                    # Verbindung wurde abgebrochen
                    socket.close()
                    self.socket_list.remove(socket)
                    del self.clients[socket]

    def run(self):
        print(f"Chat Server gestartet auf Port {self.port}")
        while True:
            # Verwendet select, um auf eingehende Verbindungen oder Nachrichten zu warten
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [], 0.1)

            for sock in ready_to_read:
                # Neue Verbindung
                if sock == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.socket_list.append(sockfd)
                    self.clients[sockfd] = addr
                    print(f"Client ({addr}) verbunden")
                # Eine Nachricht von einem Client
                else:
                    try:
                        data = sock.recv(4096).decode().strip()
                        if not data:
                            print(f"Client ({self.clients[sock]}) ist offline.")
                            sock.close()
                            self.socket_list.remove(sock)
                            del self.clients[sock]
                        if data:
                            self.broadcast(data, sock)
                    except Exception as e:
                        # Verbindung wurde abgebrochen
                        print(f"Client ({addr}) ist offline.")
                        sock.close()
                        self.socket_list.remove(sock)
                        del self.clients[sock]
                        continue

if __name__ == "__main__":
    port = 9090
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    server = ChatServer(port)
    server.run()
