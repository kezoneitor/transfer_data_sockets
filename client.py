import socket
import os

s = socket.socket()
host = 'localhost'
port = 9900
code = 'utf-8'
bufer = 2048
dir_path = os.path.dirname(os.path.realpath(__file__))

while True:
    host_port = input("insert ip and port in this format (0.0.0.0:9999) or just press 'enter' to local\n")
    if ':' in host_port:
        info = host_port.split(':')
        host, port = info[0], info[1]
        break
    elif host_port == "":
        break
    print("Your info is wrong. try again")

s.connect((host, port))

while True:
    try:
        command = input("cheese>").encode(code)
        s.send(command)
        bData = s.recv(bufer)
        data = bData.decode(code).split(' ')
        if 'closed' in data:
            s.close()
            break
        if data[0] == '-u':
            f = open(dir_path+data[1], 'rb')
            while True:
                l = f.read(bufer)
                s.send(l)
                print("send data...")
                if not l:
                    s.send(b'3nd?tr4ns')
                    break
            print(s.recv(bufer).decode(code))
            f.close()
        elif data[0] == '-d':
            d = data[1].split('/')
            #create file and write to client file
            with open(dir_path+"/download/"+d[len(d)-1], 'wb') as f:
                print('file opened', d[len(d)-1])
                while True:
                    print('receiving data...')
                    data = s.recv(bufer)
                    if data == b'3nd?tr4ns':
                        s.send(b'done')
                        break
                    # write data to a file
                    f.write(data)
                f.close()
            print(s.recv(bufer).decode(code))
        else:
            print(s.recv(bufer).decode(code))
    except Exception as e:
        print("<<ERROR>> Exception: %s" % str(e))


