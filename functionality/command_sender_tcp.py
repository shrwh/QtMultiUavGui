import socket
from qt_core import *
import re
import json
import threading


class CommandSender(QThread):

    printToCodeEditor = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = 1
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind(('', 8888))
        self.conns={}

    def run(self):
        self.socket.listen()
        while self.status==1:
            conn,addr=self.socket.accept()
            address_id=conn.recv(1024).decode()
            print(f"command_sender: Remote PC with addr[{addr}] as id[{address_id}] connected.")
            self.printToCodeEditor.emit(f"command_sender: Onboard PC with addr[{addr}] as id[{address_id}] connected.")
            temp=self.conns.get(address_id)
            if temp is not None:
                ip=temp.getpeername()[0]
                if ip!=addr[0]:
                    raise Exception("Error: Duplicate address_id of remote PC!")
                else:
                    temp.close()
            self.conns[address_id]=conn

    def _sendCommand(self,data,address_id):
        print(f"command_sender: Sending command{data} to onboard PC id[{address_id}]...")
        self.conns[address_id].sendall(data.encode())

    def sendCommand(self,command_input):
        if len(command_input) == 0:
            return
        command = command_input.strip()
        command_split=re.split("[^A-Za-z0-9_.-]+",command)
        #print(command_split)
        temp = command.find("@")
        if temp != -1:
            _command = command_split[:-1]
            address_id = command_split[-1]
            msg = json.dumps(_command)
            self._sendCommand(msg, address_id)
        else:
            for address_id in self.conns.keys():
                msg = json.dumps(command_split)
                self._sendCommand(msg, address_id)