from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

PORT = 5005
NAME = 'HandyChat'
class EndSession(Exception): pass

class CommandHandler:
    """
    Similar to cmd.Cmd in stdlib
    """
    def unknown(self, session, cmd):
        'response to unknown command'
        seesion.push('Unknown command: %s\r\n' % cmd)

    def handle(self, session, line):
        'handle the line received from specific chat'
        if not line.strip(): return
        # split command:
        parts = line.split(' ', 1)
        cmd = parts[0]
        try: line = parts[1].strip
        except IndexError: line = ''
        # try to look for handle proc
        meth = getattr(self, 'do_' + cmd, None)
        try:
            # assume it can be called
            meth(session, line)
        except TypeError:
            # if not, call this segement
            self.unknown(session, cmd)

class Room(CommandHandler):
    """
    In charge of handling basic instrutions and broadcast
    """
    def __init__(self, server):
        self.server = server
        self.session = []

    def add(self, session):
        'One client has entered room'
        self.session.append(session)

    def remove(self, session):
        'One client has left room'
        self.session.remove(session)

    def broadcast(self, line):
        'sent one line info to everyone in room'
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        'response to logout cmd'
        raise EndSession

class LoginRoom(Room):
    """
    get room ready for client just linked
    """

    def add(self, session):
        Room.add(self, session)
        # greetings when clienr enter the room
        self.broadcast('Welocome to %s\r\n' % self.server.name)

    def unknown(self, session, cmd):
        # All unknown instructions except login/logout
        # will cause a warning:
        session.push('Please log in\nUse "login <nick>"\r\n')

    def do_login(self, session, line):
        name = line.strip()
        # make sure user enter their names
        if not name:
            session.push('Please enter a name\r\n')
        # make sure no duplicated name
        elif name in self.server.user:
            session.push('The name "%s" is taken.\r\n' % name)
            session.push('Please try again\r\n')
        else:
            # no problem about name 
            # then move user to chat room
            session.name = name
            session.enter(self.server.main_room)

class ChatRoom(Room):
    """
    room for multi-users chat
    """

    def add(self, session):
        # tell everyone new user is entering
        self.broadcast(session.name + ' has enyterd the room.\r\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        Room.remove(self, session)
        # tell everyone a user has left
        self.broadcast(session.name + ' has left tne room.\r\n')

    def do_say(self, session, line):
        self.broadcast(session.name + ': ' + line + '\r\n')

    def do_look(self, session, line):
        'handle look(), check who is in the room'
        session.push('The following are in this room:\r\n')
        for other in self.session:
            session.push(other.name + '\r\n')
    
    def do_who(self, session, line):
        'check who has loged in'
        session.push('The following are logged in:\r\n')
        for name in self.server.users:
            session.push(name + '\r\n')

class LogoutRoom(Room):
    """
    simple room for single user which is 
    used to remove user from the server
    """

    def add(self, session):
        # when user enter the LogoutRoom which
        # is about to be deleted
        try: del self.server.user[session.name]
        except KeyError: pass

class ChatSession(async_chat):
    """
    single chat which is in charge of single user chat
    """
    
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        self.name = None
        # All chats start from single LoginRoom:
        self.enter(LoginRoom(server))

    def enter(self, room):
        # remove (self) from room and 
        # add himself to next room
        try: cur = self.room
        except AttributeError: pass
        else: cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []
        try: self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))

class ChatServer(dispatcher):
    """
    Single room with single server
    """

    def __init__(self, port, name):
        # Standard setup tasks
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self, line):
        conn, addr = self.accept()
        ChatSession(self, room)

if __name__ == '__main__':
    s = ChatServer(PORT, NAME)
    try: asyncore.loop()
    except KeyboardInterrupt: print