import socket
from qt_core import *
import re
import json


class CommandSender:
    def __init__(self):
        self.status = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address={}
        #self.socket.bind(('', 8003))
        #self.socket.settimeout(3)

    def _sendCommand(self,data,address):
        print(data,"to",address)
        self.socket.sendto(data.encode(),address)

    def sendCommand(self,command_input):
        if len(command_input) == 0:
            return
        command = command_input.strip()
        command_split=re.split("[^A-Za-z0-9_.]+",command)
        #print(command_split)
        temp = command.find("@")
        if temp == 0:
            addresses = command_split[1:]
            #原方案:"@192.168.xxx.1 8888 192.168.xxx.2 8888"
            # if len(addresses) > 2:
            #     address1 = (addresses[0], int(addresses[1]))
            #     self.address["a"] = self.address["1"] = address1
            #     address2 = (addresses[2], int(addresses[3]))
            #     self.address["b"] = self.address["2"] = address2
            # else:
            #     address1 = (addresses[0], int(addresses[1]))
            #     self.address["a"] = self.address["1"] = address1

            #考虑大于两台自动绑定的情况:"@192.168.xxx.1 8888 a"
            #print(addresses)
            address=(addresses[0],int(addresses[1]))
            self.address[addresses[2]]=address
        elif temp != -1:
            _command = command_split[:-1]
            address_id = command_split[-1]
            msg = json.dumps(_command)
            self._sendCommand(msg, self.address[address_id])
        else:
            for value in self.address.values():
                msg = json.dumps(command_split)
                self._sendCommand(msg, value)