#!/usr/bin/env python3

import socket
import sys
import threading

# custom modules
from compression_service import api
from compression_service.header import Header
from compression_service import errors

# constants
BUFFER = 9216   # 9 KiB
PAYLOAD_OFFSET = 8


###############################################
####### multithreading support
###############################################

class Thread(threading.Thread):

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn


    def run(self):
        '''
        receives data from socket calls service request to perform necessary actions on it
        returns server response to client
        '''

        # accept multiple requests from a thread -- is this accurate?
        while True:
            data = self.conn.recv(BUFFER)
            print('this is the data server receives', data)

            # client has no more data to send
            if not data: break

            # service request returns appropriate respone to client's request
            response = service_request(data)
            self.conn.sendall(response)



def service_request(data):
    '''
    service a request by putting data received into proper format and calling correct request
    returns response to request based on request type
    also keep track of some statistics
    '''

    # stats -- keep track of bytes received
    with api.bytes_recvd_lock:
        api.bytes_recvd += len(data)

    # initialize header object with empty values
    header = Header(0, 0)

    # deserialize data received
    status_code = header.deserialize(data)

    # problems w/ header
    if status_code == 33 or status_code == 34:
        response = errors.error(status_code)

    # no problems w/ header
    else:
        if header.code == 1:                        # ping request
            response = api.ping_req()

        elif header.code == 2:                      # get stats request
            response = api.get_stats_req()

        elif header.code == 3:                      # reset stats request
            response = api.reset_stats_req()

        elif header.code == 4:                      # compress request
            payload = data[PAYLOAD_OFFSET:]
            response = api.compress_req(payload)

        else:
            # unsupported request type
            response = errors.error(3)

    # stats -- keep track of bytes sent
    with api.bytes_sent_lock:
        api.bytes_sent += len(response)

    return response


def start_server(port):
    '''
        creates TCP socket and keeps it listening
        supports multiple clients
     '''

    host = 'localhost'               # symbolic name meaning all available interfaces
    PORT = port                      # arbitrary non-privileged port

    # create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((host, port))
        s.listen(5)

        print("Server online...")

        while True:                  # keep server listening

            try:
                conn, addr = s.accept()

                client_thread = Thread(conn)
                client_thread.start()

            except (KeyboardInterrupt, OSError):
                print("Shutting down...")
                conn.close()
                s.close()
                break


if __name__ == '__main__':

    if len(sys.argv) != 2:              # port number expected ... terminate otherwise
        print("Incorrect number of arguments. Please only enter a port number.")
        sys.exit()

    port = int(sys.argv[1])
    start_server(port)
