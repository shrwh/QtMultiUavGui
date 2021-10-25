import socket
from qt_core import *
import re
import json
import threading
import time


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
            uav_id=conn.recv(1024).decode()
            print(f"command_sender: Remote PC with addr[{addr}] as id[{uav_id}] connected.")
            self.printToCodeEditor.emit(f"command_sender: Onboard PC with addr[{addr}] as id[{uav_id}] connected.")
            temp=self.conns.get(uav_id)
            if temp is not None:
                ip=temp.getpeername()[0]
                if ip!=addr[0]:
                    print("command_sender: warning: duplicate address_id of remote PC!")
                    self.printToCodeEditor.emit(
                        "command_sender: warning: duplicate address_id of remote PC!")
                else:
                    temp.close()
            self.conns[uav_id]=conn
            if temp is None:
                receiver = threading.Thread(target=self._responseReceiver, args=(uav_id,))
                receiver.setDaemon(True)
                receiver.start()

    def _sendCommand(self,data,uav_id):
        print(f"command_sender: Sending command{data} to onboard PC id[{uav_id}]...")
        self.conns[uav_id].sendall(data.encode())

    def _responseReceiver(self,uav_id):
        while self.status==1:
            try:
                response=self.conns[uav_id].recv(1024).decode()
                # python socket的一个bug?，当对面断开连接后，recv会持续收到空字符串
                if response=="":
                    raise ConnectionResetError()
            except ConnectionResetError as e:
                time.sleep(0.5)
            else:
                print(f'command_sender: id[{uav_id}] response:\n"{response}"')
                # f'<font style="white-space: pre-line;" color=\"{color}\">{text}</font>'
                temp=f'<font style="white-space: pre-line;" color=\"black\">id[{uav_id}] response:\n</font>'\
                     +f'<font style="white-space: pre-line;" color=\"red\">{response}</font>'
                self.printToCodeEditor.emit(temp)

    def sendCommand(self,command_input):
        command = command_input.strip()
        if len(command) == 0:
            return
        command_split=re.split("[^A-Za-z0-9_.-]+",command)
        #print(command_split)
        temp = command.find("@")
        if temp != -1:
            _command = command_split[:-1]
            uav_id = command_split[-1]
            msg = json.dumps(_command)
            self._sendCommand(msg, uav_id)
        else:
            for uav_id in self.conns.keys():
                msg = json.dumps(command_split)
                self._sendCommand(msg, uav_id)

