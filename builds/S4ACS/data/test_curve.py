import zmq

server_test_key = b'rq:rM>}U?@Lns47E1%kR.o@n%FcmmsL/@{H8]yf7'

ctx = zmq.Context()
# client = ctx.socket(zmq.PULL)
client = ctx.socket(zmq.SUB)
client.subscribe("")

client_public, client_secret = zmq.curve_keypair()
client.curve_secretkey = client_secret
client.curve_publickey = client_public
client.curve_serverkey = server_test_key

client.connect('tcp://127.0.0.1:9876')
print('Waiting...')
while 1:
    print('ACK',client.recv())
