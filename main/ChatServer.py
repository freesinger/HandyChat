from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

PORT = 5005
NAME = 'HandyChat'
class EndSession(Exception): pass

class ConmmandHandler:
    """
    Similar to cmd.Cmd in stdlib
    """
    def unknown(self.session, cmd):
        'response to unknown command'
        seesion.push('Unknown command: %s\r\n' % cmd)

    def handle(self, session, line):
        'handle the line received from specific chat'
        if not line.strip(): return
        #split command:
        parts = line.split(' ', 1)
        cmd = parts[0]
        try: line = parts[1].strip
        except IndexError: line = ''
        #try to look for handle proc
        meth = getattr(self, 'do_' + cmd, None)
        try:
            #assume it can be called
            meth(session, line)
        except TypeError:
            #if not, call this segement
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
       