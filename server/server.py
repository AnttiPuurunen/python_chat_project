import socket
import selectors
import types

localIP="127.0.0.1"
serverPort=5000
buffSize=1024
totalClients=[]
sel = selectors.DefaultSelector()

def accept_connection(sock):
    # Should be ready to ready, because the server socket was registered to monitor for read events
    conn, addr = sock.accept()
    print("Connected from: " + str(addr[0]) + ":" + str(addr[1]))
    conn.setblocking(False)
    totalClients.append(conn)
    # Create an object to hold the needed data
    data = types.SimpleNamespace(addr=addr, inbound=b"", outbound=b"")
    # Monitor for read and write events
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        receive = sock.recv(buffSize)
        if receive:
            # Add data to data object to be sent later
            data.outbound += receive
        else:
            # If there's no data, the socket has been closed
            print("Closing connection: " + data.addr[0] + ":" + str(data.addr[1]))
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outbound:
            # Sends the data and returns the number of bytes sent
            for client in totalClients:
                if client != sock:
                    sent = client.send(data.outbound)
            # Discard the sent data from the buffer
            data.outbound = data.outbound[sent:]

def tcpserver():
    sckt = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) 
    sckt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sckt.bind((localIP, serverPort))
    sckt.listen()
    # Set the socket to non-blocking mode
    sckt.setblocking(False)
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