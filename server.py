from concurrent.futures import ThreadPoolExecutor
from logging import exception
from time import perf_counter
from uuid import uuid4
import grpc
import rides_pb2 as pb
import rides_pb2_grpc as rpc
from grpc_reflection.v1alpha import reflection
import validate

def new_ride_id():
    return str(uuid4().hex)

class TimingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start = perf_counter()
        try:
            return continuation(handler_call_details)
        finally:
            duration = perf_counter() - start
            name = handler_call_details.method
            print("{} took {:.2f}ms".format(name, duration * 1000))

class Rides(rpc.RidesServicer):
    def Start(self, request, context):
        try:
            validate.start_request(request)
        except validate.Error as err:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"{err.field}:{err.reason}")
            raise err
            
        ride_id  = new_ride_id()
        return pb.StartResponse(id=ride_id)
        
    def Track(self, request_iterator, context):
        count = 0
        for request in request_iterator:
            print(f"track {str(request)}")
            count += 1
        return pb.TrackResponse(count=count)

def load_credentials():
    with open("cert.pem", "rb") as f:
        cert = f.read()
    
    with open("key.pem", "rb") as f:
        key = f.read()

    return grpc.ssl_server_credentials([(key, cert)])


def build_server(port):
    server = grpc.server(
        ThreadPoolExecutor(),
        interceptors=(TimingInterceptor(),)
    )

    rpc.add_RidesServicer_to_server(Rides(), server)
    names = (
        pb.DESCRIPTOR.services_by_name['Rides'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(names, server)

    # credentials = load_credentials()
    # openssl req -newkey rsa:4096 -x509 -days 365 -nodes -subj '/CN=localhost' -keyout key.pem -out cert.pem
    # server.add_secure_port('[::]:8888', credentials)
    server.add_insecure_port(f'[::]:{port}')
    return server

if __name__ == '__main__':
    server = build_server("8888")
    server.start()
    server.wait_for_termination()