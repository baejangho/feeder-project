import socket, select
import queue
import threading
import json
import time

class Feeder_server:
    def __init__(self, ip, state_port, cmd_port):
        ## TCP/IP 기본 설정 ##
        self.server_ip = ip
        self.state_port = state_port
        self.cmd_port = cmd_port
        self.BUFFER = 4096                              # buffer max size
        
        ## 1:N TCP/IP 통신을 위한 변수 초기화 ##
        self.feeder_max_num = 10                        # max feeder num      
        # {"ID":{"feeder_ID":"F-01","feed_size":3},"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":Flase}
        self.info = {"F-01":{"feeder_ID":"F-01","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-02":{"feeder_ID":"F-02","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-03":{"feeder_ID":"F-03","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-04":{"feeder_ID":"F-04","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-05":{"feeder_ID":"F-05","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-06":{"feeder_ID":"F-06","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-07":{"feeder_ID":"F-07","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-08":{"feeder_ID":"F-08","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-09":{"feeder_ID":"F-09","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False},\
                    "F-10":{"feeder_ID":"F-10","feed_size":3,"remains":10,"feed_motor_ouput":0,\
                            "spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":False}}
                                                       
        self.feeder_socket_list = {}                    # {"F-01":socket정보}
        self.feeder_state_list = {}                     # {"F-01":True, "F-02":True, ... , "F-10":False}
        self.feeding_plan = {}                         
        # {"F-01":{'start time' : '09:00','pace' : 0,'spread':1.5, 'amount' : 1.5},'F-02':{'start time' : '16:00','pace' : 0,'spread':1.5, 'amount' : 1.5}}
        for i in self.info:
            self.feeder_state_list[i]= self.info[i]["connectitity"]
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
                        self.info_updata(data["feeder_ID"])
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
                            self.feeder_socket_list[data["ID"]] = s
                            print(self.feeder_socket_list)
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
        if ID in self.feeder_socket_list:
            sock = self.feeder_socket_list[ID]
            self.w_cmd_socks.append(sock)
            self.cmd_Queue[sock].put(cmd)
        else:
            print(ID,'는 연결되어 있지 않습니다')
            print(self.w_cmd_socks)

    def send_cmd_all(self, cmd):
        for ID in self.feeder_socket_list:
            sock = self.feeder_socket_list[ID]
            self.w_cmd_socks.append(sock)
            self.cmd_Queue[sock].put(cmd)
               
    def get_feeder_info(self,ID="F-01"):
        ## ID 급이기의 정보 반환 ##
        ## return dic -> 
        # 예) {"feeder_ID":"F-01","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":Flase}
        return self.info[ID]
            
    def get_feeder_info_all(self):
        ## 모든 급이기의 정보 반환 ##
        ## return dic -> 
        # 예) {"F-01":{"feeder_ID":"F-01","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":Flase},\
        #      "F-02":{"feeder_ID":"F-02","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":Flase},\
        #      ...
        #      "F-10":{"feeder_ID":"F-10","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectitity":Flase}}
        return self.info

    def get_online_feeder_list(self):
        ## 현재 연결 중인 급이기 ID 리스트 반환 ##
        ## return list -> 예) ["F-01","F-02"]
        feeder_list_online = []
        for i in self.info:
            if self.info[i]["connectitity"]:
                feeder_list_online.append(i)
        return feeder_list_online
    
    def get_feeder_state(self,ID):
        ## ID 급이기의 connectivity 상태 반환 ##
        ## return bool -> 예) True or False
        return self.feeder_state_list[ID]["connectitity"]
    
    def get_feeder_state_all(self):
        ## 10개 급이기의 connectivity 상태 반환 ##
        ## return dic -> 예) {"F-01":True,"F-02":True,"F-03":True, ... , "F-10":True}
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
    
    def info_updata(self,ID):
        self.feeder_state_list[ID] = self.info[ID]["connectitity"]
        


if __name__ == "__main__":
    server_ip = '192.168.0.4'
    state_port = 2200
    cmd_port = 2201
    FS = Feeder_server(server_ip, state_port, cmd_port)
    #FS.get_feeder_info()
    
    
    
