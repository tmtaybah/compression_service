# -*- coding: utf-8 -*-

import threading

# custom imports
from compression_service.header import Header
from compression_service.huffman_coding import compress
# from compression_service.compress import compress
from compression_service import errors

# stats
bytes_sent = 0
bytes_sent_lock = threading.Lock()

bytes_recvd = 0
bytes_recvd_lock = threading.Lock()

payload_bytes = 0   # what is this? apparently size before compression
compressed_bytes = 0

# a lock to be used when updating compression stats
compression_lock = threading.Lock()

# constants
MAX_PAYLOAD = 8192  # 8 KiB -- why do i have a max?


###############################################
####### REQUEST FUNCTIONS
###############################################

def ping_req():
    '''
    check service is available and operating normally
    '''

    print("PING!")

    # create appropriate response header -- status OK
    header = Header(0, 0)
    headerB = header.serialize()

    return headerB


def get_stats_req():
    '''
    returns total bytes sent, total bytes received, and compression ratio
    from service uptime or last reset
    '''

    # serialize stats
    with bytes_sent_lock:
        sentB = bytes_sent.to_bytes(4, byteorder='big')
    with bytes_recvd_lock:
        recvdB = bytes_recvd.to_bytes(4, byteorder='big')

    # calculate & serialize compression ratio
    with compression_lock:
        if payload_bytes != 0:
            compression_ratio = int((compressed_bytes / payload_bytes) * 100)
        else:   # avoid division by 0
            compression_ratio = 0

    compression_ratioB = compression_ratio.to_bytes(1, byteorder='big') # should this be inside lock?

    # print for logging purposes --> log
    print("bytes sent %d and bytes recieved %d" % (bytes_sent, bytes_recvd))

    print('payload bytes %d and compressed bytes %d' %
         (payload_bytes, compressed_bytes))
    print('compression ratio is', compression_ratio)

    payload = sentB + recvdB + compression_ratioB
    payload_len = len(payload)

    # create appropriate response header -- status OK
    header = Header(payload_len, 0)
    headerB = header.serialize()

    return headerB + payload


def reset_stats_req():
    '''
    reset all service statistics to default values
    '''

    # acquire lock, reset stats
    with bytes_sent_lock:
        global bytes_sent
        bytes_sent = 0

    with bytes_recvd_lock:
        global bytes_recvd
        bytes_recvd = 0

    with compression_lock:
        global payload_bytes
        payload_bytes = 0

        global compressed_bytes
        compressed_bytes = 0

    print("bytes sent %d & bytes recieved %d" % (bytes_sent, bytes_recvd))
    print("payload bytes %d & compressed bytes %d" %
          (payload_bytes, compressed_bytes))

    # create appropriate response header -- status OK
    header = Header(0, 0)
    headerB = header.serialize()

    return headerB


def compress_req(payload):
    print(f"payload is {payload} && type {type(payload)}")
    '''
    return a compressed version of payload using a simple prefix compression scheme
    only accepts lowercase ascii strings of a maximum length of MAX_PAYLOAD
    '''

    if len(payload) > MAX_PAYLOAD:
        return errors.error(2)


    # deserialize payload
    try:
        payload = payload.decode('ascii')

    except UnicodeDecodeError:
        print('Error: encountered non ascii characters')
        return errors.error(35)


    # returns compressed version of payload
    compressed = compress(payload)
    print('compressed VALUE is', compressed)
    payload_len = len(compressed)
    # compressedB = compressed.encode('ascii')
    compressedB = bytes(compressed)

    print(f"type is {type(compressedB)}")

    # update metrics to be able to calculate compression ratio
    with compression_lock:
        global payload_bytes
        payload_bytes += len(payload)

        global compressed_bytes
        compressed_bytes += payload_len

    # create appropriate response header -- status OK
    header = Header(payload_len, 0)
    headerB = header.serialize()
    print(f"type of headerB {type(headerB)}")

    return headerB + compressedB
