## Structure

- main.py: stuff from "tcp socket server stuff happening here"
if __name__ == '__main__':

- api.py: ping, get_stats, reset_stats, compress_req , error?

- compress.py: compress, decompress, related constants

- service.py: threading stuff, service_request

- errors.py: Contains your error definitions

## Tests

- api_test.py You need to write unit tests for each of the request types in the api.

- compress_test.py

- client.py: To test the server

## Other

1. Documentation in code & Readme (state assumptions)
2. Write requested scripts
3. Write performance benchmarks or collect performance numbers
4. Try to answer questions

## General Notes:

- Be Consistent e,g. Always use the DEBUG prints
- Add function comments/docs
- Use a better variable name than s, in compress and decompress
- maybe rename thread to client_thread?

if i want to add counter class:
<!-- # class Counter:
# # counters will be objects of this class
# # this is so that no thread will have to wait to acquire the lock to
# # do something other than what the lock is used for
#     def __init__(self):
#         self.lock = threading.Lock
#         self.value = 0
#
# bytes_sent = Counter()
# bytes_recvd = Counter()
# payload_bytes = Counter()
#compressed_bytes = Counter() -->
