from feeder_server import Feeder_server
import time

server_ip = '192.168.0.3'
state_port = 2200
cmd_port = 2201
FS = Feeder_server(server_ip, state_port, cmd_port)
while True:
    print(FS.get_feeder_info('F-01'))
    print(FS.get_feeder_list())
    time.sleep(1)