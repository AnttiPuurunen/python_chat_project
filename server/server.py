import socket
import selectors
import types

localIP="127.0.0.1"
serverPort=5000
buffSize=1024
totalClients=[]
sel = selectors.DefaultSelector()

def accept_connection(sock):
    # Should be ready to read, because the server socket was registered to monitor for read events
    conn, addr = sock.accept()
    print("Connected from: " + str(addr[0]) + ":" + str(addr[1]))
    conn.setblocking(False)
    totalClients.append(conn)
    # Create an object to hold the needed data
    # Data is already initialized as byte strings
    data = types.SimpleNamespace(addr=addr, inbound=b"", outbound=b"")
    # Monitor for read and write events
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        print("Receiving data")
        receive = sock.recv(buffSize)
        name_split = receive.decode()
        name_split.split(": ")
        isleaving = name_split[1]
        name = name_split[0]
        print(len(name_split))
        if len(name_split) == 1:
            # A new client joined, notify everybody else
            userjoined = f"{name} joined the chat room"
            data.outbound += userjoined.encode()
        elif isleaving == "quit":
            # The client has closed the client program, close the sock
            # Send everyone else notification that they left
            userleft = f"{name} has left the chat room"
            data.outbound += userleft.encode()
            sel.unregister(sock)
            sock.close()
        elif receive:
            # Add data to data object to be sent later
            data.outbound += receive
        else:
            # If there's no data, the socket has been closed
            print("Closing connection: " + data.addr[0] + ":" + str(data.addr[1]))
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outbound:
            print("Sending data")
            sent=None
            # Sends the data and returns the number of bytes sent
            for client in totalClients:
                if client != sock:
                    sent = client.send(data.outbound)
            # Discard the sent data from the buffer
            print(sent)
            if sent:
                data.outbound = data.outbound[sent:]
            else:
                data.outbound = b""

def tcpserver():
    sckt = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) 
    sckt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sckt.bind((localIP, serverPort))
    sckt.listen()
    print("In server, socket listening...")

    # Monitor the socket for read events
    sel.register(sckt, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    # If there's no data, the event is from the server socket
                    # Establish a new socket connection
                    accept_connection(key.fileobj)
                else:
                    # There is a connection, handle read/write events
                    # Key has the socket object and data, mask contains info on the operations that are ready
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        sel.close()      

if __name__ == "__main__":
    tcpserver()     