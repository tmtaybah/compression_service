# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import pytest

from multiprocessing import Process

from compression_service.header import Header
from compression_service.server import start_server


HOST = ''
PORT = 50000       # static port number


###############################################
####### setup
###############################################


@pytest.fixture(scope="module")
def server():

    server = Process(target=start_server, args=(PORT,))
    server.start()
    time.sleep(0.5)       # was join
    # server.join(0)      # apparently as long as I put a value here, conn wont be refused .... so why doesnt it work with timeout=None?

    return server



@pytest.fixture(scope="module")
def client(server):

    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((HOST, PORT))

    yield c

    c.close()
    server.terminate()

###############################################
####### helper functions
###############################################

def deserialize_stats(payload):

    sentB = payload[0:4]
    sent = int.from_bytes(sentB, byteorder='big')

    recievedB = payload[4:8]
    recv = int.from_bytes(recievedB, byteorder='big')

    compB = payload[8:]
    comp = int.from_bytes(compB, byteorder='big')


    return (sent, recv, comp)



def deserialize_payload(payload):

    payload = payload.decode('ascii')

    return payload


###############################################
####### test functions
###############################################


def test_bad_magic_val(client):
    '''
    send a ping request with an incorrect magic value
    should result in error 33
    '''

    bad_magic_val = 0x53545250
    payload_len = 0
    req_code = 1

    # serialize header data
    magic_valueB = bad_magic_val.to_bytes(4, byteorder='big', signed=True)
    payload_lenB = payload_len.to_bytes(2, byteorder='big', signed=True)
    req_codeB = req_code.to_bytes(2, byteorder='big', signed=True)

    # manual creation of serialized header
    header = magic_valueB + payload_lenB + req_codeB
    client.sendall(header)
    data = client.recv(1024)

    # create empty header, deserialize data into it
    response_header = Header(0, 0)
    response_header.deserialize(data)

    got = (response_header.payload_len, response_header.code)
    expected = (0, 33)  # expecting status code 33 -- bad magic value error

    assert got == expected



def test_unsupported_req(client):
    '''
    create a header with an unsupported request code/type
    should result in error 3
    '''

    header = Header(0, 5)
    client.sendall(header.serialize())
    data = client.recv(1024)

    # create empty header, deserialize data into it
    response_header = Header(0, 0)
    response_header.deserialize(data)

    got = (response_header.payload_len, response_header.code)
    expected = (0, 3)       # expecting status code 3 -- unsupported request error

    assert got == expected



def test_ping(client):
    '''
    testing ping request function
    should receive response header with status 0 -- OK
    '''

    ping_header = Header(0, 1)
    client.sendall(ping_header.serialize())
    data = client.recv(1024)

    # create empty header, deserialize data into it
    response_header = Header(0, 0)
    response_header.deserialize(data)

    got = (response_header.payload_len, response_header.code)
    expected = (0, 0)

    assert got == expected



def test_unexpected_payload_len(client):
    '''
    testing error 34 where payload length specified in header does not match
    payload length receive
    '''

    ping_header = Header(5, 1)
    client.sendall(ping_header.serialize())
    data = client.recv(1024)

    # create empty header, deserialize data into it
    response_header = Header(0, 0)
    response_header.deserialize(data)

    got = (response_header.payload_len, response_header.code)
    expected = (0, 34)

    assert got == expected



def test_reset(client):
    '''
    test reset stats request by calling reset stats and check reset stats result by calling get stats
    expected value is 8, 8, 0 because we also call get stats
    '''

    # testing reset_stas
    reset_header = Header(0, 3)
    client.sendall(reset_header.serialize())
    reset_data = client.recv(1024)        # server response to rest stats request


    # create empty header, deserialize data into it -- bytes_recvd += 8
    reset_response_header = Header(0, 0)
    reset_response_header.deserialize(reset_data)

    got = (reset_response_header.payload_len, reset_response_header.code)
    expected = (0, 0)

    assert got == expected      # checking that server returned OK

    # call get stats request to check reset stats actually works -- bytes_sent += 8
    stats_header = Header(0, 2)
    client.sendall(stats_header.serialize())

    # server response to get stats request
    stats_data = client.recv(1024)

    # create empty header, deserialize data into it
    stats_response_header = Header(0, 0)
    stats_response_header.deserialize(stats_data)

    expected = (9, 0) # get stat's payload should be 9 bytes
    got = (stats_response_header.payload_len, stats_response_header.code)

    assert got == expected


    expected = (8, 8, 0) # Only one req/rsp of header size since reset.
    got = deserialize_stats(stats_data[8:])

    assert got == expected



def test_get_stats(client):
    '''
    test get stats request by reseting stats and calling ping 3 times to be able predict output
    '''

    # reset stats (without compression ratio)-- they will now be 8, 8, 0
    test_reset(client)

    i = 0
    while i < 3:
        test_ping(client)
        i += 1

    stats_header = Header(0, 2)
    client.sendall(stats_header.serialize())

    # server response to get stats request
    stats_data = client.recv(1024)

    # create empty header, deserialize data into it
    stats_response_header = Header(0, 0)
    stats_response_header.deserialize(stats_data)

    expected = (9, 0) # get stat's payload should be 9 bytes
    got = (stats_response_header.payload_len, stats_response_header.code)

    assert got == expected


    ping_bytes = 3 * 8

    # Only one req/rsp of header size since reset.
    expected = (8 + (8 + 9) + ping_bytes , 8 + 8 + ping_bytes, 0)
    got = deserialize_stats(stats_data[8:])

    assert got == expected



def test_compress_req_max(client):
    '''
    give compress request a string with length more than max payload
    should result in error 2 -- message too large
    '''

    # Test Max payload
    max_payload = b'a' * 8193
    compress_header = Header(8193, 4)
    client.sendall(compress_header.serialize() + max_payload)
    compress_data = client.recv(1024)

    # create empty header, deserialize data into it
    compress_response_header = Header(0, 0)
    compress_response_header.deserialize(compress_data)

    expected = (0, 2)
    got = (compress_response_header.payload_len, compress_response_header.code)

    assert got == expected


# fix
# def test_compress_ratio(client):
#     '''
#     compress 3 strings, check server returns payload length == compressed length
#     generating stats for compression ratio to use
#     '''
#
#     # (payload, compressed length)
#     payloads = [ (b'aaaabbbbbcccccc', 6),
#                  (b'hhhhhheeeeellllllloooooooooooooooooo', 9),
#                  (b'fffffdddddddddddd', 5)]
#
#     payload_count = 0.0
#     compressed_count = 0.0
#
#     for payload in payloads:
#         # update stats to be able to calculate compression ratio
#         payload_count += len(payload[0])
#         compressed_count += payload[1]
#
#
#         compress_header = Header(len(payload[0]), 4)
#         client.sendall(compress_header.serialize() + payload[0])
#         compress_data = client.recv(1024)
#
#         # create empty header, deserialize data into it
#         compress_response_header = Header(0, 0)
#         compress_response_header.deserialize(compress_data)
#
#         # expecting server to return compressed string with status OK
#         expected = (payload[1], 0)
#         got = (compress_response_header.payload_len, compress_response_header.code)
#
#         assert got == expected
#
#
#     ## checking compression ratio by calling get stats
#
#     stats_header = Header(0, 2)
#     client.sendall(stats_header.serialize())
#
#     # server response to get stats request
#     stats_data = client.recv(1024)
#
#     # create empty header, deserialize data into it
#     stats_response_header = Header(0, 0)
#     stats_response_header.deserialize(stats_data)
#
#     expected = (9, 0) # get stat's payload should be 9 bytes
#     got = (stats_response_header.payload_len, stats_response_header.code)
#
#     assert got == expected
#
#     # calculate compression ratio, check against compression ratio returned by get stats
#     expected = int((compressed_count / payload_count) * 100)
#     got = deserialize_stats(stats_data[8:])[2]
#
#     assert got == expected



def test_compress(client):

    string = b'go go go go gophers gopher gophers'

    payload_len = len(string)
    compress_header = Header(payload_len, 4)

    client.sendall(compress_header.serialize() + string)
    compress_resp = client.recv(1024)

    # create empty header, deserialize data into it
    compress_response_header = Header(0, 0)
    compress_response_header.deserialize(compress_resp)
    compressed = compress_resp[8:]

    expected = b'-\xf6r\xd0\xb9\xd9K\x95\xc2@\x0c\x02t\xe9\xd3\xa6\xcb\xca\xe9\xb2\xf3\xa6\xcb\xca'

    assert compressed == expected
