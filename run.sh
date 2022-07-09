# generate components
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. rides.proto

# run server
python server.py

# use grpcurl to test the server
grpcurl -plaintext localhost:8888 list
grpcurl -plaintext localhost:8888 describe Rides.Start
grpcurl -plaintext localhost:8888 describe .StartRequest
grpcurl -plaintext -d @ localhost:8888 Rides.Start < request.json
grpcurl -plaintext -d @ localhost:8888 Rides.Start < bad_request.json
grpcurl -insecure -d @ localhost:8888 Rides.Start < request.json

# running client
python client.py

# generate openssl certificate
openssl req -newkey rsa:4096 -x509 -days 365 -nodes -subj '/CN=localhost' -keyout key.pem -out cert.pem

#run tests
python -m pytest -v