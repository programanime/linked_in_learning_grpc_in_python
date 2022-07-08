import rides_pb2 as pb
from datetime import datetime
from google.protobuf.json_format import MessageToJson
import json
from google.protobuf.timestamp_pb2 import Timestamp

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


time = datetime(2022, 1, 1, 12, 0, 0)
request.time.FromDatetime(time)

print(request)

data = json.loads(MessageToJson(request))


time2 = request.time.ToDatetime()
print("this is the time : ", time2)
print("type:", type(data))
print("size:", len(data))
print("this is my nested location", request.location.lat)
print("this is the driver_id", data.get("driver_id"))
now = Timestamp()
now.GetCurrentTime()
print(now)


