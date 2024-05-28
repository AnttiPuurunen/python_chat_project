import socket
import threading
from tkinter import *

localIP="127.0.0.1"
serverPort=5000
buffSize=1024
messages = []
th_list=[]

root=Tk()
root.title("Chat client")
root.columnconfigure(0, weight=1, minsize=250)
root.rowconfigure(0, weight=1, minsize=100)
root.rowconfigure(1, weight=1, minsize=250)
root.rowconfigure(2, weight=1, minsize=50)

name=""
sock=None

def onconnectclick(event="<Return"):
    name=entry_name.get()
    if (len(name) > 0):
        sock = client_socket()
        #print("Going to destroy intro window")
        #for widget in root.winfo_children():
         #   widget.destroy()
        msg_list.insert(END, f"{name} joined the chat room")
        users_list.insert(END, name)
        return sock
    
intro_frame=Frame(root)
intro_frame.grid(row=0, column=0, padx=10, pady=10)
name_label=Label(intro_frame, text="Give username").pack()
entry_name=Entry(intro_frame)
entry_name.bind("<Return>", onconnectclick)
entry_name.pack()

connect_button=Button(intro_frame, text="Connect")
connect_button.bind("<Button-1>", onconnectclick)
connect_button.pack(pady=10)

def send_msg(event="<Return>"):
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
messages_frame.grid(row=1, column=0)
msg_scrollbar = Scrollbar(messages_frame)
# Here's where the messages will appear
msg_list = Listbox(messages_frame, font="Helvetica", fg="black", height=20, width=50, yscrollcommand=msg_scrollbar.set)
users_list = Listbox(messages_frame, font="Helvetica", fg="black", height=20, width=20)
users_list.pack(side=RIGHT, padx=5, fill=BOTH)
msg_scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, padx=5, fill=BOTH)

entry_frame=(Frame(root))
entry_frame.grid(row=2, column=0)
msg_entry = Entry(entry_frame)
msg_entry.bind("<Return>", send_msg)
msg_entry.pack(side=LEFT, fill=X)
send_button=Button(entry_frame, text="Send")
send_button.bind("<Button-1>", send_msg)
send_button.pack(side=RIGHT, padx=10)

def on_quit():
    # Send the server a message to close the connection before exiting
    msg_entry.insert(0, "quit")
    send_msg()
    sock.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_quit)

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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.connect(server_addr)

send_name = name + ": "
sock.send(str.encode(name + ": ")) 

def client_socket():

    # Create separate threads for sending and receiving messages
    th=threading.Thread(target=send_msg, args=()).start()  
    th_list.append(th)
    th=threading.Thread(target=recv_msg, args=()).start()
    th_list.append(th)

if __name__ == "__main__":
    root.mainloop()