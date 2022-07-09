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
