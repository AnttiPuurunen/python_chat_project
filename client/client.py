import sys
import socket
import selectors
import threading

localIP="127.0.0.1"
serverPort=5000
buffSize=1024
messages = []
th_list=[]

def send_msg(sock, name):
    data = input(name + ": ")
    sock.send(str.encode(name + ": " + data))

def recv_msg(sock):
    while True:
        data = sock.recv(buffSize)
        print(data.decode())

def start_connection():
    server_addr = (localIP, serverPort)
    
    print(f"Connecting to server {server_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_addr)

    return sock

def client_socket():
    sock=None
    try:
        sock=start_connection()
    except:
        print("Connection failed")
        sys.exit()

    name = input("Please give a username: \n")
    # Create separate threads for sending and receiving messages
    th=threading.Thread(target=send_msg, args=(sock, name)).start()  
    th_list.append(th)
    th=threading.Thread(target=recv_msg, args=(sock,)).start()
    th_list.append(th)
    
    runClient=True 
    try:
        while runClient:
            send_msg(sock, name)
    except KeyboardInterrupt:
        runClient=False
        print("Exiting...")
    finally:
        sock.close()
        for th in th_list:
            th.join() 

if __name__ == "__main__":
    client_socket()