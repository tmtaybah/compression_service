# -*- coding: utf-8 -*-

''' this client is for interactive testing purporses '''

import sys
import socket
import threading

from compression_service.header import Header
from compression_service import errors


def deserialize_payload(payload, request_code):

    if request_code == 2:   # get stats request

        sentB = payload[0:4]
        sent = int.from_bytes(sentB, byteorder='big')

        recievedB = payload[4:8]
        recv = int.from_bytes(recievedB, byteorder='big')

        compB = payload[8:]
        comp = int.from_bytes(compB, byteorder='big')

        return f" Bytes sent = {sent} & Bytes received = {recv} & Compression ratio = {comp}"

    else:   # compression request
        payload = payload.decode('ascii')
        return payload


def send_request(socket, code):

    # compression request requires payload
    if code == 4:
        payload = input('enter a string to compress: ')
        payloadB = payload.encode('ascii')
        payload_len = len(payloadB)

    # create request header, serialize it, and send it
        header = Header(payload_len, code)
        socket.sendall(header.serialize() + payloadB)

    else:
        header = Header(0, code)
        socket.sendall(header.serialize())


def get_response(s, code):

    # Receive response
    data = s.recv(9216)
    print("this is the response recieved from server: ", data)  # log?

    # create header & init w/ empty values
    header = Header(0, 0)
    header.deserialize(data)

    # print error msgs
    if header.code in errors.error_codes:
        print('ERROR: ', errors.error_codes.get(header.code))

    else:
        print('payload length = ', header.payload_len)
        print('status code = ', header.code)

        # payload is only present for get stats or compress requests
        if header.code == 2 or header.code == 4:
            payload = data[8:]
            deserialize_payload(payload, code)


if __name__ == '__main__':

    # HOST and PORT must be passed in ... program terminates otherwise
    if len(sys.argv) != 3:
        print("Please enter only a host followed by a port number")
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    # create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            try:
                code = int(input("Request Code? "))
                send_request(s, code)
                get_response(s, code)

            except (KeyboardInterrupt, OSError):
                s.close()
                break
