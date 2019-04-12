from compression_service.header import Header


error_codes = {1: 'Unknown error', 2: 'Message too large',
               3: 'Unsupported request type',
               33: 'Magic value does not match expected magic value',
               34: 'Actual payload length does not match expected payload length',
               35: 'Invalid: contains non-ascii characters'}


def error(error_code):
    '''
    prints error msg & returns response header with appropriate status code
    '''

    # print error msg for logging purposes
    print("ERROR: "+ error_codes.get(error_code))

    header = Header(0, error_code)
    headerB = header.serialize()

    return headerB
