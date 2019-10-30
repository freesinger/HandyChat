"""
Generate class ChatsServer which should inherit the class dispathcher in module asyncore
Dispathcher basically is a socket object
This server does nothing 
"""
from asyncore import dispatcher
import asyncore

class ChatServer(dispatcher): pass

s = ChatServer()
asyncore.loop()