# Compression Service


## Description (High Level of inner workings)

* server creates a socket and a thread for each client that connects to it, it then launches a thread which effectively receives the data from the client and hands it off to service_request to deal with appropriately.
* service_request creates a header object header object that contains magic value, payload length, and request/status code. Header can also serialize and deserialize its contents (this streamlines receiving and responding to requests).
* based on the request code in the header object service_request calls the relevant api function.
* finally service_request keeps track of some statistics by incrementing bytes received when it's first called with data and bytes sent before sending the response that results from calling the api functions, all variables that keep track of statistics are shared variables across multiple threads and so are locked before being read or written to.
* service_request's response is sent to the client over the TCP socket  


## Target Platform & Language

- MacOS 10.13
- also tested on Ubuntu 16.04
- python3

## Assumptions

* assumes compress takes a lowercase string with no whitespace
* stats is across multiple clients (e.g. for the entire service)
* get stats request returns service statistics at the time of request and does not reflect the bytes used to send get stats response but it does reflect the bytes received in with get stats request  
* any prints are mainly for logging purposes
* header values are interpreted as signed integers and statistical values are interpreted as unsigned

## Third Party Libraries
- pytest : simplifies testing

## Instructions

### Building

`./build.sh`

### Running  

`./run.sh`

### Testing

#### Unit test (pytest)

`make test`

#### Interactive testing   
on two terminal sessions:
1. `./run.sh`
2. `make run_client`


## Improvements

* formalize the logging process by having server write to a file the packets it receives and packets it sends and any error messages generated, all time-stamped
* adding performance measurements to understand how many requests/sec the service can handle.


## things to do:

* fix max_payload issue

* remove all instances of magic value

* add decompress request? what would be purpose? just for testing or is it actually needed?

* add code to change port if current port unavailable in make .. possible?
