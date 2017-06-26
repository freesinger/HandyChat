from asyncore import dispatcher
import socket, asyncore

class ChatServer(dispatcher):

    #handle_accept() prints info of any attemp link 
    def handle_accept(self):
        conn, addr = self.accept()
        #addr[0] is the IP of guest
        print 'Connection attemp from', addr[0]

s = ChatServer()
s.create_socket(socket.AF_INET, socket.SOCK_STREAM)
#'' means all interfaces of 'localhost', 5005 is the port number
s.bind(('', 5005))
#5 means 5 tasks needed to be handle
s.listen(5)
#listen in a rotation
asyncore.loop()