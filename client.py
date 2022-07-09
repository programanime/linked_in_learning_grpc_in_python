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
