from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

PORT = 5005
NAME = 'HandyChat'
class ChatSession(async_chat):
    """
    handle a class between a server and a client
    """
    def __init__(self, server, sock):
        #standard set task:
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        #greetings to client
        self.push('Welcome to %s\r\n' % self.server.name)
    
    def collect_incoming_data(self, data):
        self.data.append(data)
    
    def found_terminator(self):
        """
        if find a terminater means a whole line is readed, broadcast to everyone
        """
        line = ''.join(self.data)
        self.data = []
        self.server.broadcast(line)

    def handle_close(self):
        async_chat.handle_close(self)
        self.server.disconnect(self)

class ChatServer(dispatcher):
    """
    handle link and form single chat class
    """
    def __init__(self, port, name):
        #Standard setup tasks
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.name = name
        self.session = []
    def disconnect(self, session):
        self.session.remove(session)

    def broadcast(self, line):
        for session in self.session:
            session.push(line + '\r\n')
    
    def handle_accept(self, line):
        conn, addr = self.accept()
        self.session.append(ChatSession(self, conn))

if __name__ == '__main__':
    s = ChatServer(PORT, NAME)
    try: asyncore.loop()
    except KeyboardInterrupt: print