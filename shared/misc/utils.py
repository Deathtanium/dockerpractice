import socket
import threading
import logging as log

def read_till_null(sock:socket.socket):
    data = b''
    while True:
        d = sock.recv(1024)
        if not d:
            break
        data += d
        if b'\0' in d:
            break
    data = data[:-1]
    return data

class ThreadedServer(object):
    def __init__(self, host:str, port:int, f_response, log_file:str):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.f_response = f_response
        fh = log.FileHandler(log_file)
    
    def listen(self):
        self.sock.listen(5)
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()
    
    def handle_client(self, client:socket.socket, addr):
        while True:
            try:
                data = read_till_null(client)
                if data:
                    self.f_response(data)
                else:
                    log.info('thread_handler - connection closed by {}'.format(addr))
                client.close()
            except Exception as e:
                log.error('thread_handler - {}'.format(e))
                client.close()
                break