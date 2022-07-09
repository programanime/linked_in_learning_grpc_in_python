# grpc
# links
[scalar types](https://developers.google.com/protocol-buffers/docs/proto3#scalar)  
[official documentation for python](https://grpc.github.io/grpc/python/grpc.html)  
[git curl](https://github.com/fullstorydev/grpcurl)  


# RPC
* Remote Procedure Call
    - call a function on a remote server

# Why?
- scale
- security
- upgrades
- wire in any language
![](img/rpc_why.png)  

# parts
- serialization format
- transport

# GRPC parts
## protocol buffers
 - faster than json
## http/2
 - faster than http/1.1 
 [demo](http://www.http2demo.io/)
 - higher throughput
 - multiplexing
 - request prioritization
 - server push


 ![](img/21580.png)  
  
 - require libraries
[file](file:b:/grpc/grpc_in_python/requirements.txt)
```pip-requirements
google-api-python-client~=2.45
grpcio-reflection~=1.44
grpcio-tools~=1.44
grpcio~=1.44
protobuf~=3.20
pytest~=7.1
```

# grpc ecosystem
## streaming
## double streaming

# messages
- data structure
[file](file:b:/grpc/grpc_in_python/rides.proto)
```proto3
syntax="proto3";

message StartRequest {
    int64 car_id = 1;
    string driver_id = 2;
    repeated string passengers_ids = 3;
}
```

## convert proto files
 - you need to use proto buffer compiler
 - each time you change the message you need to recompile the file
```shell
protoc rider.proto --python_out=. 
```

## defining your own messages in python 
 - right after you complete the message you need to set the message on python

 - you define the message calling one method
[file](file:b:/grpc/grpc_in_python/app.py)
```python
import rides_pb2 as pb
request = pb.StartRequest(
    car_id = 1,
    driver_id = "daniel",
    passengers_ids = ["p1", "p2"],
    type = pb.POOL,
    location = pb.Location(
        lat = -23.5,
        lng = -46.6,
    )
)

print(request)
```

## access to request data
getting values from the request object, you could access to any value

[file](file:b:/grpc/grpc_in_python/app.py)
```python
request.car_id
```
## define the service
 - you need to define the service, input and output

[file](file:b:/grpc/grpc_in_python/rides.proto)
```proto3
service Rides{
    rpc Start(StartRequest) returns (StartResponse) {}
}
```

```shell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. rides.proto
```

# reflection

[file](file:b:/linked_in_learning_grpc_in_python/server.py)
```python
    reflection.enable_server_reflection(names, server)
```

# curl for making requests
- curl commands  

[file](file:b:/linked_in_learning_grpc_in_python/run.sh)  

```shell
grpcurl -plaintext localhost:8888 list
grpcurl -plaintext localhost:8888 describe Rides.Start
grpcurl -plaintext localhost:8888 describe .StartRequest
grpcurl -plaintext -d @ localhost:8888 Rides.Start < request.json
grpcurl -plaintext -d @ localhost:8888 Rides.Start < bad_request.json
```

# validate

[file](file:b:/linked_in_learning_grpc_in_python/validate.py)
```python
class Error(ValueError):
    def __init__(self, field, reason):
        super().__init__(f"{field}:{reason}")
        self.field = field
        self.reason = reason

def start_request(request):
    if not request.driver_id:
        raise Error("driver_id", "empty")
    #TODO: validate more fields
```

# grpc client

[file](file:b:/linked_in_learning_grpc_in_python/client.py)
```python
import grpc
import rides_pb2_grpc as rpc
import rides_pb2 as pb
from datetime import datetime

class Client():
    def __init__(self, address):
        self.channel = grpc.insecure_channel(address)
        self.stub = rpc.RidesStub(self.channel)

    def close(self):
        self.channel.close()
    
    def ride_start(self, car_id, driver_id, passengers_ids, type, lat, lng, time):
        request = pb.StartRequest(
            car_id=car_id,
            driver_id=driver_id,
            passengers_ids=passengers_ids,
            type=pb.POOL if type == "POOL" else pb.REGULAR,
            location=pb.Location(lat=lat, lng=lng),
        )
        request.time.FromDatetime(time)
        try:            
            response = self.stub.Start(request)
        except grpc.RpcError as err:
            raise grpc.RpcError(f"{err.code()}: {err.details()}") 
        return response.id
    
if __name__ == '__main__':
    address = f'localhost:8888'
    
    client = Client(address)
    ride_id = client.ride_start(
        car_id=1,
        driver_id="driver_id",
        passengers_ids=["passenger_id"],
        type="POOL",
        lat=1.0,
        lng=1.0,
        time=datetime.now()
    )

    print(ride_id)
```
# for yield
- go through data in a stream

[file](file:b:/linked_in_learning_grpc_in_python/lab.py)
```python
def rand_events(count):
    for number in range(count):
        yield {"number":number}
        sleep(1)

for x in rand_events(10):
    print(x)
```

# stream client and server
1. edit rides.proto
    - define messages
[file](file:b:/linked_in_learning_grpc_in_python/rides.proto)
```proto3
message TrackRequest {
    int64 car_id = 1;
    google.protobuf.Timestamp time = 2;
    Location location = 3;
}

message TrackResponse {
    uint64 count = 1;
}
```
2. define server methods

[file](file:b:/linked_in_learning_grpc_in_python/rides.proto)
```proto3
    rpc Track(stream TrackRequest) returns (TrackResponse);
```

3. get stream events
[file](file:b:/linked_in_learning_grpc_in_python/events.py)
```python
from collections import namedtuple
from datetime import datetime, timedelta
from time import sleep

LocationEvent = namedtuple("LocationEvent", "car_id time lat lng")

def rand_events(count):
    time = datetime(2022, 2, 22, 14, 36, 9)
    lat, lng = 1.0, 1.0
    for _ in range(count):
        yield LocationEvent(
            car_id = 7,
            time=time,
            lat=lat,
            lng=lng
        )

        time += timedelta(seconds = 17)
        lat += 0.0001
        lng -= 0.0001
        sleep(0.1)
```

4. define track method in the client and start to track events
[file](file:b:/linked_in_learning_grpc_in_python/client.py)
```python
    def track(self, events):
        return self.stub.Track(track_request(event) for event in events)

def track_request(event):
    request = pb.TrackRequest(
        car_id=event.car_id,
        location=pb.Location(lat=event.lat, lng=event.lng),
    )
    request.time.FromDatetime(event.time)
    return request
```

5. consume stream events
[file](file:b:/linked_in_learning_grpc_in_python/client.py)
```python
def consume_stream_client(client):
    events = rand_events(10)
    try:
        response = client.track(events) 
        print(f"getting some anwer {response}")
    except Exception as err:
        print("error"+str(err))

```

[file](file:b:/linked_in_learning_grpc_in_python/client.py)
```python
address = f'localhost:8888'
    client = Client(address)
```

[file](file:b:/linked_in_learning_grpc_in_python/client.py)
```python
    consume_stream_client(client)
```

pretty useful to send continuous data

# interceptors
- let you intercept all the requests to the server

[file](file:b:/linked_in_learning_grpc_in_python/server.py)
```python
from time import perf_counter
```

[file](file:b:/linked_in_learning_grpc_in_python/server.py)
```python
class TimingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start = perf_counter()
        try:
            return continuation(handler_call_details)
        finally:
            duration = perf_counter() - start
            name = handler_call_details.method
            print("{} took {:.2f}ms".format(name, duration * 1000))
```

[file](file:b:/linked_in_learning_grpc_in_python/server.py)
```python
server = grpc.server(
        ThreadPoolExecutor(),
        interceptors=(TimingInterceptor(),)
    )
```

# https 
[text](https://openssl.org)

- generate certificate
[file](file:b:/linked_in_learning_grpc_in_python/openssl_generator.sh)
```shell
openssl req -newkey rsa:4096 -x509 -days 365 -nodes -subj '/CN=localhost' -keyout key.pem -out cert.pem
```

- load credentials file
[file](file:b:/learning_linkedin_grpc_in_python/server.py)
```python
def load_credentials():
    with open("cert.pem", "rb") as f:
        cert = f.read()
    
    with open("key.pem", "rb") as f:
        key = f.read()

    return grpc.ssl_server_credentials([(key, cert)])
```

- get the files and open secure port
[file](file:b:/learning_linkedin_grpc_in_python/server.py)
```python
    credentials = load_credentials()

    server.add_secure_port('[::]:8888', credentials)
```

# share .proto files, for any one to build their one client

## monorepo
everything in one repo

## git submodule
 - put some dependencies into your project

```shell
git submodule add https://github.com/anjeyy/grpc-sample
```

## distributing python modules

# pytest for grpc

- test starting the server
- test consuming one grpc method

[file](file:b:/learning_linkedin_grpc_in_python/test_server.py)
```python
from socket import socket
from unittest.mock import MagicMock
from datetime import datetime
import grpc
import pytest
import rides_pb2 as pb
import rides_pb2_grpc as rpc
from server import build_server
import server as svr

def test_start():
    request = pb.StartRequest(
        car_id = 7,
        driver_id = "John Doe",
        passengers_ids = ["M", "Q"],
        type = pb.POOL,
        location = pb.Location(lat = 51.46, lng = -0.2),
    )

    request.time.FromDatetime(datetime(2022, 1, 1, 12, 0, 0))
    context =  MagicMock()

    rides = svr.Rides()
    resp  = rides.Start(request, context)
    assert resp.id != ""

def free_port():
    with socket() as sock:
        sock.bind(('localhost', 0))
        _, port = sock.getsockname()
        return port

@pytest.fixture()
def conn():
    port = free_port()
    server = build_server(port)
    server.start()

    with grpc.insecure_channel(f"localhost:{port}") as channel:
        stub = rpc.RidesStub(channel)
        yield server, stub

    server.stop(grace=0.1)

def test_start_server(conn):
    server, stub = conn

    request = pb.StartRequest(
        car_id = 7,
        driver_id = "John Doe",
        passengers_ids = ["M", "Q"],
        type = pb.POOL,
        location = pb.Location(lat = 51.46, lng = -0.2),
    )

    request.time.FromDatetime(datetime(2022, 1, 1, 12, 0, 0))
    response = stub.Start(request)
    assert response.id != ""

```
