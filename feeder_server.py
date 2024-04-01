import socket, select
import queue
import threading
import json
import time

class Feeder_server:
    def __init__(self, ip, state_port, cmd_port):
        
        self.sock_list = []                             # event socket list
        self.BUFFER = 4096                              # buffer max size
        self.feeder_max_num = 10                        # max feeder num
        self.feeder_full_list = ["F-01", "F-02", "F-03", "F-04", "F-05", "F-06", "F-07", "F-08", "F-09", "F-10"]
        self.server_ip = ip
        self.state_port = state_port
        self.cmd_port = cmd_port
        self.info = {}
        self.feeder_list = {}                           # {"ID":socket정보}
        self.feeder_state_list = {}                     # {"ID":'connect'}
        self.feeding_plan = {}                         
        # {"F-01":{'start time' : '09:00','pace' : 0,'spread':1.5, 'amount' : 1.5},'F-02':{'start time' : '16:00','pace' : 0,'spread':1.5, 'amount' : 1.5}}
        for i in self.feeder_full_list:
            self.feeder_state_list[i]= 'disconect'
        print(self.feeder_state_list)
                                 
        self.initialize_socket()        
    
    def initialize_socket(self):
        self.state_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmd_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.state_server_socket.setblocking(0)
        self.cmd_server_socket.setblocking(0)
        self.state_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.cmd_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            
        self.state_server_socket.bind((self.server_ip, self.state_port))
        self.cmd_server_socket.bind((self.server_ip, self.cmd_port))
        self.state_server_socket.listen(self.feeder_max_num)
        self.cmd_server_socket.listen(self.feeder_max_num)
        
        self.state_Queue = {}                                       # {소켓 : 메시지큐}
        self.cmd_Queue = {}                                         # {소켓 : 메시지큐}
        self.r_state_socks = [self.state_server_socket]
        self.r_cmd_socks = [self.cmd_server_socket]
        self.w_cmd_socks = []
        
        state_th = threading.Thread(target = self.state_server_thread)
        cmd_th = threading.Thread(target = self.cmd_server_thread)
        #state_th.daemon = True
        state_th.start()
        cmd_th.start()
    
    def state_server_thread(self):
        while self.r_state_socks:
            #print('state test')
            readEvent, writeEvent, errorEvent = select.select(self.r_state_socks, [], self.r_state_socks, 1)
            
            for s in readEvent:                                     # 읽기 가능 소켓 조사
                if s is self.state_server_socket:                   # 서버 소켓?
                    print("client 접속 중")
                    c_sock, c_address = s.accept()
                    print(c_sock, "가 접속함")
                    c_sock.setblocking(0)
                    self.r_state_socks.append(c_sock)
                    #print(self.r_state_socks)
                    #self.state_Queue[c_sock] = queue.Queue()        # FIFO 큐 생성
                else:                                               # 클라이언트 소켓?  
                    try:
                        data = s.recv(self.BUFFER)
                        data = json.loads(data)
                        #self.state_Queue[s].put(data)
                        #print('state :',data)
                        self.info[data["feeder_ID"]] = data          
                    except:                                           # 연결이 종료되었는가?
                        self.r_state_socks.remove(s)
                        s.close()
                        #del self.state_Queue[s]
            
            for s in errorEvent:                                    # 오류 발생 소켓 조사
                self.r_state_socks.remove(s)                        # 수시 소켓 목록에서 제거
                s.close()
                del self.state_Queue[s]
    
    def cmd_server_thread(self):
        while self.r_cmd_socks:
            #print('cmd test')
            readEvent, writeEvent, errorEvent = select.select(self.r_cmd_socks, self.w_cmd_socks, self.r_cmd_socks, 1)
            
            for s in readEvent:                                     # 읽기 가능 소켓 조사
                if s is self.cmd_server_socket:                     # 서버 소켓?
                    print("cmd client 접속 중")
                    c_sock, c_address = s.accept()
                    print(c_sock, "가 접속함")
                    c_sock.setblocking(0)
                    self.cmd_Queue[c_sock] = queue.Queue()          # FIFO 큐 생성 self.cmd_Queue = {c_sock : (que),c_sock2 : (que)}
                    self.cmd_Queue[c_sock].put("ID")
                    self.r_cmd_socks.append(c_sock)
                    if s not in self.w_cmd_socks:
                        self.w_cmd_socks.append(c_sock)
                    
                else:                                               # 클라이언트 소켓?
                    try:
                        data = s.recv(self.BUFFER)
                        data = json.loads(data)
                        if "ID" in data:
                            print('test ID')
                            self.feeder_list[data["ID"]] = s
                            print(self.feeder_list)
                        else:
                            print('test중')
                    except:
                        print('error 발생')
                        if s in self.w_cmd_socks:
                            self.w_cmd_socks.remove(s)
                        self.r_cmd_socks.remove(s)
                        s.close()
                        del self.cmd_Queue[s]
            
            for s in writeEvent:                                    # 쓰기 가능 소켓 조사        
                print('cmd send test')
                try:
                    next_msg = self.cmd_Queue[s].get_nowait()        # cmd 큐에서 메시지 인출
                except: #queue.Empty():
                    self.w_cmd_socks.remove(s)                      # 송신 소켓 목록에서 제거
                else:
                    s.send(next_msg.encode())
            
            for s in errorEvent:                                    # 오류 발생 소켓 조사
                self.r_cmd_socks.remove(s)                        # 수시 소켓 목록에서 제거
                if s in self.w_cmd_socks:
                    self.w_cmd_socks.remove(s)
                s.close()
                del self.cmd_Queue[s]
                
    def send_cmd(self, cmd, ID='F-01'):
        if ID in self.feeder_list:
            sock = self.feeder_list[ID]
            self.w_cmd_socks.append(sock)
            self.cmd_Queue[sock].put(cmd)
        else:
            print(ID,'는 연결되어 있지 않습니다')
            print(self.w_cmd_socks)

    def send_cmd_all(self, cmd):
        for ID in self.feeder_list:
            sock = self.feeder_list[ID]
            self.w_cmd_socks.append(sock)
            self.cmd_Queue[sock].put(cmd)
               
    def get_feeder_info(self,ID='F-01'):
        if ID in self.info:
            return self.info[ID]
        else:
            print(ID,'는 연결되어 있지 않습니다')
            
    def get_feeder_info_all(self):
        return self.info

    def get_feeder_list(self):
        return list(self.info.keys())
    
    def get_feeder_state(self):
        feeder_list = self.get_feeder_list
        for i in self.feeder_full_list:
            if i in feeder_list:
                self.feeder_state_list[i]= 'conect'
            else:
                self.feeder_state_list[i]= 'disconect'
        return self.feeder_state_list

    def stop_feeding(self, ID='F-01'):
        self.send_cmd("stop", ID)

    def stop_feeding_all(self):
        self.send_cmd_all("stop")
    
    def set_feeding_plan(self, ID='F-01'):
        self.feeding_plan = {0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},
                             1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}}


    def set_feeder_ID(self,addr, id):
        # 추후 제작
        pass

    def set_feeding_mode(self, mode='auto', ID='F-01'):
        self.send_cmd(mode, ID)
    
    def set_feeding_mode_all(self, mode='auto'):
        self.send_cmd_all(mode)
        
    def set_feed_size(self, size, ID='F-01'):
        cmd = 'size'+str(size)
        self.send_cmd(cmd, ID)


if __name__ == "__main__":
    def API_test():
        while True:
            ID = input("ID:")
            cmd = input("cmd:")
            FS.send_cmd(cmd,ID)
            #time.sleep(2)

    server_ip = '192.168.0.4'
    state_port = 2200
    cmd_port = 2201
    FS = Feeder_server(server_ip, state_port, cmd_port)
    #FS.get_feeder_info()
    main_th = threading.Thread(target = API_test)
    main_th.start()
    
