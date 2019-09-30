import socket
import threading
import time
from datetime import datetime
import os 

all_connections = []
all_address = []
now_backlog = 0
max_backlog = 5
code = 'utf-8'
bufer = 2048

# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = "localhost"
        port = 9900
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# Binding the socket and listening for connections
def bind_socket():
    try:
        global now_backlog
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(1)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

# Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py file is restarted
def accepting_connections():
    global now_backlog
    global max_backlog
    global code
    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout
            if now_backlog > max_backlog:
                close_connection(con, address, 0)
            else:
                now_backlog += 1
                all_connections.append(conn)
                all_address.append(address)
                t = threading.Thread(target=cheese_transfer,args=(conn, address,))
                t.daemon = True
                t.start()
        except:
            print("Error accepting connections")

#Close one connection 
def close_connection(conn, address, type = 1):
    global now_backlog
    try:
        if type == 0:
            conn.send("connections are full. Your connection was closed".encode(code))
        elif type == 1:
            conn.send("Thanks for used. Your connection was closed".encode(code))
        else:
            print("connection fail")
        now_backlog -= 1
        conn.close()
        all_connections.remove(conn)
        all_address.remove(address)
    except Exception as e:
        print("<ERROR>", e)

#Download data
def download(conn, data, bData):
    try:
        conn.send(bData)
        f = open("."+data[1], 'rb')
        while True:
            l = f.read(bufer)
            conn.send(l)
            print("send data...")
            if not l:
                conn.send(b'3nd?tr4ns')
                break
        f.close()
        conn.recv(bufer)
        conn.send(("download this file: " + data[1]).encode(code))
    except Exception as e:
        conn.send("Error to upload file".encode(code))

#Upload data
def upload(conn, data, bData):
    try:
        #prepare client to send file
        conn.send(bData)
        d = data[1].split('/')
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d%m%Y_%H%M%S")
        #create file and write to client file
        with open("./"+dt_string+"_"+d[len(d)-1], 'wb') as f:
            print('file opened', d[len(d)-1])
            while True:
                print('receiving data...')
                data = conn.recv(bufer)
                if data == b'3nd?tr4ns':
                    break
                # write data to a file
                f.write(data)
            f.close()
        conn.send("File upload successfully.".encode(code))
    except Exception as e:
        conn.send("Error to upload file".encode(code))

#Create list files
def get_list_file(text, root_file):
    for file in os.listdir(root_file):
        text += root_file+'/'+file+'\n'
        if os.path.isdir(file):
            text = get_list_file(text, root_file+'/'+file)
    return text

#Transfer function
def cheese_transfer(conn, address):
    while True:
        try:
            bData = conn.recv(bufer)
            data = bData.decode(code).split(' ')
            size = len(data)
            if data[0] == "quit":
                break
            if size > 2:# most parameters
                conn.send("most parameters. try again".encode(code))
            elif data[0] == '':
                conn.send("less parameters. try again".encode(code))
            elif data[0] == '-d':#download
                download(conn, data, bData)
            elif data[0] == '-u':#upload
                upload(conn, data, bData)
            elif data[0] == '-l':  # list
                conn.send(bData)
                list_file = get_list_file('', '.')
                conn.send((list_file).encode(code))
            else:
                conn.send(bData)
                conn.send(("The command "+data[0]+" don't exist. try again").encode(code))
        except socket.error as e:
            close_connection(conn, address)
    close_connection(conn, address)


if __name__ == "__main__":
    create_socket()
    bind_socket()
    accepting_connections()
