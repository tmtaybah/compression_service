''' this client is for testing purporses '''

import socket
import sys
import threading
from header import Header
import errors


class Thread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        ''' receive data and deserialize it'''

        while True:
            data = self.conn.recv(9216)
            print("this is the response recieved from server: ", data)

            # create header & init w/ empty values
            header = Header(0, 0)
            header.deserialize(data)

            # print error msg
            if header.code in errors.error_codes:
                print('ERROR: ', errors.error_codes.get(header.code))

            else:
                print('payload length = ', header.payload_len)
                print('status code = ', header.code)

                # payload is only present for get stats or compress requests
                if code == 2 or code == 4:
                    payload = data[8:]
                    deserialize_payload(payload, code)



def deserialize_payload(payload, request_code):

    if request_code == 2:   # get stats request

        sentB = payload[0:4]
        sent = int.from_bytes(sentB, byteorder='big')

        recievedB = payload[4:8]
        recv = int.from_bytes(recievedB, byteorder='big')

        compB = payload[8:]
        comp = int.from_bytes(compB, byteorder='big')

        print('Bytes sent = %d & Bytes received = %d & Compression ratio = %d' %(sent, recv, comp))


    else:   # compression request
        payload = payload.decode('ascii')
        print('Compressed value = ', payload)



if __name__ == '__main__':

    if len(sys.argv) != 3:              # checking to see if user entered HOST and PORT ... program terminates otherwise
        print("Please enter only a host followed by a port number")
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    # create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # create a thread for responses
        thread = Thread(s)
        thread.start()

        while True:
            code = int(input())     # request code

            # compression request requires payload
            if code == 4:
                payload = input('enter a string to compress: ')
                payloadB = payload.encode('ascii')
                payload_len = len(payloadB)

            # create request header, serialize it, and send it
                header = Header(payload_len, code)
                s.sendall(header.serialize() + payloadB)

            else:
                header = Header(0, code)
                s.sendall(header.serialize())
