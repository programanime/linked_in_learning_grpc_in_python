from concurrent.futures import ThreadPoolExecutor
from logging import exception
from uuid import uuid4
import grpc
import rides_pb2 as pb
import rides_pb2_grpc as rpc
from grpc_reflection.v1alpha import reflection
import validate

def new_ride_id():
    return str(uuid4().hex)

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

if __name__ == '__main__':
    server = grpc.server(ThreadPoolExecutor())
    rpc.add_RidesServicer_to_server(Rides(), server)
    names = (
        pb.DESCRIPTOR.services_by_name['Rides'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(names, server)
    server.add_insecure_port('[::]:8888')
    server.start()
    server.wait_for_termination()