# -*- coding: utf-8 -*-

import socket, select
import queue
import threading
import json
import time
import feeder_variables
import schedule

class Feeder_server:
    def __init__(self, ip, state_port, cmd_port):
        ## TCP/IP 기본 설정 ##
        self.server_ip = ip
        self.state_port = state_port
        self.cmd_port = cmd_port
        self.BUFFER = 40960                                     # buffer max size

        ## 주요 변수 초기화
        self.feeder_max_num = 10                                # 총 급이기 수 = 10개로 가정     
        self.info = feeder_variables.info                       # 모든 급이기 info 초기화
        self.feeding_auto_plan = feeder_variables.auto_plan     # 모든 급이기 auto_plan 초기화
        
        ## 급이기 auto_plan에 따른 스케줄러 설정 ##
        for feeder, jobs in self.feeding_auto_plan.items():
            for job in jobs.values():
                schedule.every().day.at(job['start time']).do(self.feeding_start, feeder, job)
                                                 
        self.feeder_socket_list = {}                            # 급이기 ID와 client socket 저장 예) {"F-01":socket정보}  
        self.feeder_state_list = {}                             # 급이기 ID의 연결상태 저장 예) {"F-01":True, "F-02":True, ... , "F-10":False}
        for i in self.info:
            self.feeder_state_list[i]= self.info[i]["connectivity"]
                                 
        self.initialize_socket()        
    
    def initialize_socket(self):
        ## socket 관련 ##
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
        
        ## 1:N TCP/IP 통신을 위한 변수 초기화 ##
        self.cmd_Queue = {}                                         # {소켓 : 메시지큐}
        self.r_state_socks = [self.state_server_socket]
        self.r_cmd_socks = [self.cmd_server_socket]
        self.w_cmd_socks = []
        
        ## Thread start - main thread 종료 시 모두 종료(타이드풀과 협의 필요)
        state_th = threading.Thread(target = self.state_server_thread)
        cmd_th = threading.Thread(target = self.cmd_server_thread)
        state_th.daemon = True
        cmd_th.daemon = True
        state_th.start()
        cmd_th.start()

    ## TCP/IP 통신을 위한 서버 스레드 ##
    def state_server_thread(self):
        while self.r_state_socks:
            readEvent, writeEvent, errorEvent = select.select(self.r_state_socks, [], self.r_state_socks, 5)
            
            for s in readEvent:                                      
                if s is self.state_server_socket: # 서버 소켓에서 읽기 이벤트 발생                   
                    print("client 접속 중")
                    c_sock, c_address = s.accept()
                    print(c_sock, "가 접속함")
                    c_sock.setblocking(0)
                    self.r_state_socks.append(c_sock)
                else: # 클라이언트 소켓에서 읽기 이벤트 발생  
                    try:
                        data = s.recv(self.BUFFER)
                        data = json.loads(data)
                        #print(time.strftime("%y/%m/%d %H:%M:%S"),'-',data)
                        self.info[data["feeder_ID"]] = data
                        self.info_updata(data["feeder_ID"])
                 
                    except:                                         # 연결이 종료되었는가?
                        self.r_state_socks.remove(s)
                        print('state_th : client',s,'연결이 종료되었습니다.')
                        s.close()
            
            for s in errorEvent:                                    # 오류 발생 소켓 조사
                self.r_state_socks.remove(s)                        # 수시 소켓 목록에서 제거
                s.close()
    
    def cmd_server_thread(self):
        while self.r_cmd_socks:
            ## 스케줄 확인 ##
            schedule.run_pending()
            
            ## cmd 소켓 조사 ##
            readEvent, writeEvent, errorEvent = select.select(self.r_cmd_socks, self.w_cmd_socks, self.r_cmd_socks, 1)
            
            for s in readEvent:                                     # 읽기 가능 소켓 조사
                if s is self.cmd_server_socket:                     # 서버 소켓?
                    print("cmd client 접속 중")
                    c_sock, c_address = s.accept()
                    print(c_sock, "가 접속함")
                    c_sock.setblocking(0)
                    cmd = {"type":"ID",
                           "cmd":"",
                           "value":""}
                    self.cmd_Queue[c_sock] = queue.Queue()          # FIFO 큐 생성 self.cmd_Queue = {c_sock : (que),c_sock2 : (que)}
                    self.cmd_Queue[c_sock].put(cmd)
                    self.r_cmd_socks.append(c_sock)
                    if s not in self.w_cmd_socks:
                        self.w_cmd_socks.append(c_sock) 
                else:                                               # 클라이언트 소켓 : 급이기에서 보낸 메시지 확인
                    try:
                        data = s.recv(self.BUFFER)
                        data = json.loads(data)
                        if data["type"] == "ID":
                            self.feeder_socket_list[data["cmd"]] = s
                            print(self.feeder_socket_list)
                        else:
                            print('test중')
                    except:
                        print(s)
                        ID = self.get_key_from_value(self.feeder_socket_list, s)
                        print(ID)
                        self.info[ID]["connectivity"] = False
                        del self.feeder_socket_list[ID]
                        
                        if s in self.w_cmd_socks:
                            self.w_cmd_socks.remove(s)
                        self.r_cmd_socks.remove(s)
                        s.close()
                        del self.cmd_Queue[s]
                        print('cmd_th : client',s,'연결이 종료되었습니다.')
            
            for s in writeEvent:                                    # 쓰기 가능 소켓 조사        
                try:
                    next_msg = self.cmd_Queue[s].get_nowait()       # cmd 큐에서 메시지 인출
                except: # queue.Empty():
                    self.w_cmd_socks.remove(s)                      # 송신 소켓 목록에서 제거
                else:
                    json_state_msg = json.dumps(next_msg)
                    s.sendall(json_state_msg.encode('UTF-8'))
            
            for s in errorEvent:                                    # 오류 발생 소켓 조사
                self.r_cmd_socks.remove(s)                          # 수시 소켓 목록에서 제거
                if s in self.w_cmd_socks:
                    self.w_cmd_socks.remove(s)
                s.close()
                del self.cmd_Queue[s]
                
    ## get 함수 ##               
    def get_feeder_info(self,ID="F-01"):
        ## ID 급이기의 정보 반환 ##
        ## return dic -> 
        # 예) {"feeder_ID":"F-01","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectivity":Flase}
        return self.info[ID]
            
    def get_feeder_info_all(self):
        ## 모든 급이기의 정보 반환 ##
        ## return dic -> 
        # 예) {"F-01":{"feeder_ID":"F-01","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectivity":Flase},\
        #      "F-02":{"feeder_ID":"F-02","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectivity":Flase},\
        #      ...
        #      "F-10":{"feeder_ID":"F-10","feed_size":3,"remains":10,"feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop","event":"nothing","connectivity":Flase}}
        return self.info

    def get_online_feeder_list(self):
        ## 현재 연결 중인 급이기 ID 리스트 반환 ##
        ## return list -> 예) ["F-01","F-02"]
        feeder_list_online = []
        self.get_feeder_state_all()
        for i in self.feeder_state_list:
            if self.feeder_state_list[i]:
                feeder_list_online.append(i)
        return feeder_list_online
    
    def get_feeder_state(self,ID):
        ## ID 급이기의 connectivity 상태 반환 ##
        ## return bool -> 예) True or False
        self.get_feeder_state_all()
        return self.feeder_state_list[ID]
    
    def get_feeder_state_all(self):
        ## ID 급이기의 connectivity 상태 반환 ##
        ## return bool -> 예) True or False
        for i in self.info:
            self.feeder_state_list[i]= self.info[i]["connectivity"]
        #print(self.feeder_state_list)
        return self.feeder_state_list

    ## control 함수 ##
    def stop_feeding(self, ID='F-01'):
        cmd = {"type":"control",
               "cmd":"stop",
               "value":""}
        self.send_cmd("stop", ID)

    def stop_feeding_all(self):
        cmd = {"type":"control",
               "cmd":"stop",
               "value":""}
        self.send_cmd_all(cmd)
    
    def manual_feeding(self, pace, dist, amount, ID='F-01'):
        cmd = {"type":"control","cmd":"manual","value":{"feeding_pace":pace,"feeding_distance":dist,"feeding_amount":amount}}
        self.send_cmd(cmd, ID)
        
    def manual_feeding_all(self, pace, dist, amount):
        cmd = {"type":"control","cmd":"manual","value":{"feeding_pace":pace,"feeding_distance":dist,"feeding_amount":amount}}
        self.send_cmd_all(cmd)
   
    ## set 함수 ##
    def set_feeding_plan(self, plan, ID='F-01'): 
        ## ID 급이기의 auto_plan 설정 ##
        #  plan = {0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},
        #          1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}}
        self.feeding_auto_plan[ID] = plan
        ## 스케줄러 재설정 ##
        for feeder, jobs in self.feeding_auto_plan.items():
            for job in jobs.values():
                schedule.every().day.at(job['start time']).do(self.feeding_start, feeder, job)
    
    def set_feeding_plan_all(self, allplan): 
        ## ID 급이기의 auto_plan 설정 ##
        #  allplan = {"F-01":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                   1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},\
        #           "F-02":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                   1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-03":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                   1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-04":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                   1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-05":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                    1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-06":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                     1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-07":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                    1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-08":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                  1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},
        #           "F-09":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                     1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}},\
        #           "F-10":{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},\
        #                  1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}}}
        self.feeding_auto_plan = allplan
        ## 스케줄러 재설정 ##
        for feeder, jobs in self.feeding_auto_plan.items():
            for job in jobs.values():
                schedule.every().day.at(job['start time']).do(self.feeding_start, feeder, job)

    def set_feeder_ID(self,addr, id):
        # do not need now "
        pass

    def set_feeding_mode(self, mode='auto', ID='F-01'):
        cmd = {"type":"set",
               "cmd":"mode",
               "value":mode}
        self.send_cmd(cmd, ID)
    
    def set_feeding_mode_all(self, mode='auto'):
        cmd = {"type":"set",
               "cmd":"mode",
               "value":mode}
        self.send_cmd_all(cmd)
        
    def set_feed_size(self, size, ID='F-01'):
        cmd = {"type":"set",
               "cmd":"size",
               "value":size}
        self.send_cmd(cmd, ID)
    
    def set_feed_size_all(self, size):
        cmd = {"type":"set",
               "cmd":"size",
               "value":size}
        self.send_cmd_all(cmd)

    ## 내부 함수 ##    
    def info_updata(self,ID):
        ## feeder_state_list 업데이트 ##
        self.feeder_state_list[ID] = self.info[ID]["connectivity"]

    def feeding_start(self,feeder, job):
        print(job)
        self.get_feeder_state_all()
        if self.feeder_state_list[feeder]:
            print('feeding start')
            cmd = {"type":"control",
                   "cmd":"start",
                   "value":{"feeding_pace":job["pace"],"feeding_distance":job["spread"],"feeding_amount":job["feed amount"]}}
            self.send_cmd(cmd, feeder)

    def send_cmd(self, cmd, ID='F-01'):
        if ID in self.feeder_socket_list:
            sock = self.feeder_socket_list[ID]
            self.w_cmd_socks.append(sock)
            self.cmd_Queue[sock].put(cmd)
        else:
            print(ID,'는 연결되어 있지 않습니다')
            #print(self.w_cmd_socks)

    def send_cmd_all(self, cmd):
        for ID in self.feeder_socket_list:
            if self.feeder_socket_list[ID]:
                sock = self.feeder_socket_list[ID]
                self.w_cmd_socks.append(sock)
                self.cmd_Queue[sock].put(cmd)
            else:
                print(ID,'는 연결되어 있지 않습니다')

    def get_key_from_value(self, dictionary, target_value):
        for key, value in dictionary.items():
            if value == target_value:
                return key
        return None    
if __name__ == "__main__":
    #server_ip = '192.168.0.4'
    server_ip = '127.0.0.1'
    state_port = 2200
    cmd_port = 2201
    FS = Feeder_server(server_ip, state_port, cmd_port)
    #FS.get_feeder_info()
    try:
        while True:
            #print('test 중')
            time.sleep(10)
            
    except KeyboardInterrupt:
        print('사용자종료')
    
    
    
