import sys
import socket
import threading
from tkinter import *

localIP="127.0.0.1"
serverPort=5000
buffSize=1024
messages = []
th_list=[]

root=Tk()
root.title=("Chat client")
intro_frame=Frame(root)
intro_frame.pack(fill="both", expand=True)
name_label=Label(intro_frame, text="Give username").pack()
entry_name=Entry(intro_frame)
entry_name.pack()
name=""
sock=None

def onconnectclick():
    name=entry_name.get()
    if (len(name) > 0):
        sock = client_socket()
        #print("Going to destroy intro window")
        #for widget in root.winfo_children():
         #   widget.destroy()
        return sock

connect_button=Button(intro_frame, text="Connect", command=onconnectclick).pack()

def send_msg():
    data = msg_entry.get()
    name = entry_name.get()
    if (len(data) > 0):
        print("onsend: " + data)
        msg_entry.delete(0, END)
        data = name + ": " + data
        # Add the user's message to the list, as it won't be broadcast back to the sender
        msg_list.insert(END, data)
        sock.send(str.encode(data)) 

print("Entering chat room")
messages_frame=Frame(root)
msg_scrollbar = Scrollbar(messages_frame)
# Here's where the messages will appear
msg_list = Listbox(messages_frame, font="Helvetica", fg="black", height=20, width=70, yscrollcommand=msg_scrollbar.set)
msg_scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, fill=BOTH)
messages_frame.pack()

entry_frame=(Frame(root))
msg_entry = Entry(entry_frame)
msg_entry.pack()
send_button=Button(entry_frame, text="Send", command=send_msg)
send_button.pack()
entry_frame.pack()

def recv_msg():
    print("Recv_msg")   
    while True:
        try: 
            data = sock.recv(buffSize)
            data = data.decode()
            msg_list.insert(END, data)
        except KeyboardInterrupt:
            print("Exit...")    

server_addr = (localIP, serverPort)
    
print(f"{name} connecting to server {server_addr}")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.connect(server_addr)

def client_socket():

    # Create separate threads for sending and receiving messages
    th=threading.Thread(target=send_msg, args=()).start()  
    th_list.append(th)
    th=threading.Thread(target=recv_msg, args=()).start()
    th_list.append(th)

if __name__ == "__main__":
    root.mainloop()