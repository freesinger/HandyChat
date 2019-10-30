class EndSession(Exception): pass

class Room(CommandHandler):
    """
    In charge of handling basic instrutions and broadcast
    """
    def __init__(self, server):
        self.server = server
        self.session = []

    def add(self, session):
        self.session.append(session)

    def remove(self, session):
        self.session.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        raise EndSession