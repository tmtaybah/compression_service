# -*- coding: utf-8 -*-

class Header:

    MAGIC_VALUE = 0x54415241    # remove
    DEBUG = False

    def __init__(self, payload_len, code): # default values?
        self.payload_len = payload_len  # in bytes
        self.code = code


    def serialize(self):
        ''' prepare header for transport -- convert from int to bytes -- FORMAT'''

        magic_valueB = self.MAGIC_VALUE.to_bytes(4, byteorder='big', signed=True)   # remove
        payload_lenB = self.payload_len.to_bytes(2, byteorder='big', signed=True)
        codeB = self.code.to_bytes(2, byteorder='big', signed=True)

        headerB = magic_valueB + payload_lenB + codeB

        return headerB

    def deserialize(self, data):
        ''' deserialize takes data and extracts the header relevant parts of it into the header object
            it also deserializes them then checks for some basic errors like magic value mismatch and
            payload length recieved does not match expected length FORMAT '''
        '''returns a status code based on that FORMAT '''

        # extract header from data recieved
        magic_valueB = data[:4]              # 4 bytes
        payload_lenB = data[4:6]             # 2 bytes
        codeB = data[6:8]                    # 2 bytes

        # convert header data from bytes to int
        magic_value = int.from_bytes(magic_valueB, byteorder='big', signed=True)
        if magic_value != self.MAGIC_VALUE:
            return 33       # magic value error

        self.payload_len = int.from_bytes(payload_lenB, byteorder='big', signed=True)
        if len(data[8:]) != self.payload_len:
            return 34       # expected length != actual length

        # if all looks OK continue deserializing
        self.code = int.from_bytes(codeB, byteorder='big', signed=True)

        return 0    # all is good .. no error
