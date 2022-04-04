import asyncio
from os import system
import pickle
from Socket import Socket
import sqlite3 as sql



class Client(Socket):
    def __init__(self, username):
        super(Client, self).__init__()
        self.username = username
        self.text = ""

    def set_up(self):
        try:
            self.socket.connect(("127.0.0.1", 1234))
            self.socket.setblocking(False)
            self.socket.send(username.encode("utf-8"))
        except ConnectionRefusedError:
            print("Sorry server is offline")
            exit(0)
    async def listen_socket(self, listened_socket=None):

        while True:
            data = await self.main_loop.sock_recv(self.socket, 2048)
            self.text = f"""{data.decode("utf-8")}"""

            print(self.text)
    async def send_data(self, data=None):
        while True:
            data = await self.main_loop.run_in_executor(None, input)
            await self.main_loop.sock_sendall(self.socket, data.encode("utf-8"))


    async def main(self):
        listening_task = self.main_loop.create_task(self.listen_socket())

        sending_task = self.main_loop.create_task(self.send_data())

        await asyncio.gather(listening_task, sending_task)

if __name__ == '__main__':
    done = False

    conn = sql.connect('users.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS USERS
         (USERNAME CHAR(50) PRIMARY KEY,
         PASSWORD CHAR(50));''')

    cursor = conn.cursor()



    while done==False:
        print("============================================================\n\n")
        print("1. Log in ")
        print("2. Sign Up ")
        print("0. Exit")
        option = int(input("Choose option: "))

        if option==1:
            username = str(input("username: "))
            password = str(input("password: "))

            cursor.execute("SELECT 1 FROM Users WHERE username = '%s' AND password = '%s'" % (username, password))
            data = cursor.fetchall()
            if len(data) == 0:
                print("no such user named %s"%username)
            else:
                client = Client(username)
                client.set_up()
                client.start()

        elif option==2:
            username = str(input("username: "))
            password = str(input("password: "))
            cursor.execute("SELECT 1 FROM Users WHERE username = '%s' AND password = '%s'" % (username, password))
            data = cursor.fetchall()
            if len(data) == 0:
                cursor.execute("INSERT INTO USERS (USERNAME, PASSWORD) VALUES ('%s', '%s')" % (username, password))
                conn.commit()
            else:
                print("Such username already exist")

        else:
            conn.close()
            done=True

