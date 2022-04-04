
import asyncio
import socket

from Socket import Socket
import json
import os
clients = {}

class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()#create server
        self.users = []

    def set_up(self):

        self.socket.bind(("127.0.0.1", 1234))
        self.socket.listen(5)
        self.socket.setblocking(False)

        print("Server is listening")

    async def send_data(self, data=None, username=None, listened_socket=None):

        if username == None:
            for user in self.users:
                await self.main_loop.sock_sendall(user, data)
        else:
            value_list_d = list(clients.values())
            key_list =list(clients.keys())
            value_list = []

            for i in value_list_d:
                value_list.append(i.decode("utf-8"))
            data = clients[listened_socket]+": ".encode("utf-8")+data
            username= str(username.decode("utf-8"))
            if username in value_list:
                position = value_list.index(username)
                user = key_list[position]
                await self.main_loop.sock_sendall(user, data)
            else:
                print("No such client in server")
    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return

        while True:
            try:

                data = await self.main_loop.sock_recv(listened_socket, 2048)
                messenger = list(json.load(open('messenger.json')))
                if data.decode("utf-8") == "/allMessage":
                    if len(messenger)==0:
                        print("Sorry it's new chat there are no message")
                    else:
                        allMessage = str("")
                        for i in messenger:
                              allMessage=allMessage+str(i)+"\n"
                        await self.send_data(allMessage.encode("utf-8"))
                elif data.decode("utf-8")[:8] == "/private":
                    data = data.decode("utf-8")
                    text = data.split()

                    sending_data = ""

                    username = text[1]
                    username = username.encode("utf-8")

                    for i in range(2, len(text)):
                        sending_data+=text[i]+" "
                    await self.send_data(sending_data.encode("utf-8"), username, listened_socket)
                else:
                    data = clients[listened_socket]+": ".encode("utf-8") + data
                    print(f"""{data.decode("utf-8")}""")
                    if len(messenger)==0:
                        with open("messenger.json",'w') as messengerWF:
                            json.dump(data.decode('utf-8'),messengerWF)
                    else:
                        with open("messenger.json", 'w') as messengerWF:

                            text = messenger
                            text.append(str(data.decode('utf-8')))
                            json.dump(text,messengerWF)
                    await self.send_data(data)
            except ConnectionResetError:
                print("%s removed"%clients[listened_socket].decode("utf-8"))
                del clients[listened_socket]
                self.users.remove(listened_socket)

                return

    async def handle_client(self, user_socket=None, address=None):
        while True:
            nickname = await self.main_loop.sock_recv(user_socket, 20)
            if user_socket in clients.keys():
                print("That user already exist")
            else:
                clients[user_socket] = nickname


    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(self.socket)
            print(f"User {address[0]} connected")
            self.users.append(user_socket)
            self.main_loop.create_task(self.handle_client(user_socket, address))
            self.main_loop.create_task(self.listen_socket(user_socket))


    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())


if __name__ == '__main__':
    server = Server()
    server.set_up()

    server.start()
