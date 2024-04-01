import socket, select
import queue
import threading
import json
import time


class Feeder_server:
    def __init__(self, ip, port):
        self.fifo_Q = queue.Queue()                     # FIFO 큐 생성
        self.sock_list = []                             # event socket list
        self.BUFFER = 4096                              # buffer max size
        self.feeder_max_num = 10                        # max feeder num
        self.server_ip = ip
        self.server_port = port
        self.initialize_socket()
    
    def initialize_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        #self.state_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(self.feeder_max_num)
        self.r_socks = [self.server_socket]                 # 수신 소켓 목록, 서버 소켓 추가
        self.w_socks = []                                   # 송신 소켓 목록
        self.msgQueue = {}                                  # 메시지 큐 목록 {소켓:메시지큐}
        self.server_start()                                 # 서버 start
    
    def server_start(self):
        while self.r_socks:   
            R_Event, W_Event, E_Event = select.select(self.r_socks, self.w_socks, self.r_socks)

            for sock in R_Event:                        # 읽기 가능 소켓 조사
                if sock is self.server_socket:          # 서버 소켓인가?
                    c_sock, c_addr = sock.accept()
                    c_sock.setblocking(0)
                    self.r_socks.append(c_sock)
                else:                                   # 클라이언트 소켓인가?
                    data = sock.recv(self.BUFFER)
                    if data:
                        data = json.loads(data)
                        print(data)
                    else:
                        if sock in self.w_socks:
                            self.w_socks.remove(sock)
                        self.r_socks.remove(sock)
                        sock.close()



    
    def get_feeder_info(self):
        
        while True:
            print('get')
            try:
                data = self.state_client_socket.recv(self.BUFFER)
                print(data)
                if data:
                    data = json.loads(data)
                    print(data)
                else:
                    print('error')
                    self.self.stat_client_socket.close()
                    #self.cmd_server_socket.close()
                    break
            finally:
                self.state_server_socket.close()
                self.cmd_server_socket.close()
            #    break

    def start_feeding(self):
        pass

    def stop_feeding(self):
        pass

    def set_feeder_ID(self,addr, id):



if __name__ == "__main__":
    server_ip = '192.168.0.3'
    state_port = 2200
    cmd_port = 2201
    FS = Feeder_server(server_ip, state_port, cmd_port)
    FS.get_feeder_info()
    while True:
        print('test')
        time.sleep(2)
