# -*- coding: utf-8 -*-

import socket
import threading
import json
import time
#from feeder_loadcell_test import Loadcell

class Feeder_client:
    def __init__(self, ip, state_port=2200, cmd_port=2201):
        ## TCP/IP 설정 ##
        self.ip = ip                                                    # server ip
        self.state_port = state_port                                                # server port
        self.cmd_port = cmd_port                                                    # server port
        self.BUFFER = 10240                                                         # buffer max size
        
        ## feeder parameter 초기화 ##
        self.feeder_ID = 'F-01'
        self.weight = 0
        self.feed_size = 3
        self.feed_motor_pwm = 0
        self.spread_motor_pwm = 0
        self.isTerminate = False
        self.feed_mode = 'stop'                                                     # 'stop' 'auto' 'manual'
        self.state_event_period = 1 # sec
        self.feeder_event = 'nothing'
        
        self.event = threading.Event()
        self.init_set() 
    
    def initialize_socket(self):
        try:
            self.event.clear() 
            self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # state socket 생성
            self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # state socket 생성
            #self.state_socket.settimeout(10)
            #self.cmd_socket.settimeout(10)
            self.state_socket.connect((self.ip, self.state_port))                    # server로 연결 요청
            self.cmd_socket.connect((self.ip, self.cmd_port))
            #self.state_socket.settimeout(None)
            #self.cmd_socket.settimeout(None)
            self.cmd_thread()
            self.state_thread()
            self.control_thread()
        except:
            print('서버와 연결되지 않았습니다.')
            self.init_set()
    
    def init_set(self):
        print('서버와 접속을 시도합니다')
        self.feed_motor_pwm = 0
        self.spread_motor_pwm = 0
        time.sleep(2)
        self.initialize_socket() 

    def state_thread(self):
        state_th = threading.Thread(target = self.state_event)
        state_th.daemon = True
        state_th.start()
        
    def cmd_thread(self):
        cmd_th = threading.Thread(target = self.cmd_event)
        cmd_th.daemon = True
        cmd_th.start()
    
    def control_thread(self):
        cmd_th = threading.Thread(target = self.control_event)
        cmd_th.daemon = True
        cmd_th.start()        
    
    def state_event(self):
        # 급이기 정보 server로 전달 #
        while not self.event.is_set():
            try:
                s_time = time.time()
                print('send state')
                message = {'feeder_ID':self.feeder_ID,
                           'feed_size':self.feed_size,
                           'remains':self.weight,
                           'feed_motor_output':self.feed_motor_pwm,
                           'spread_motor_output':self.spread_motor_pwm,
                           'feed_mode':self.feed_mode,
                           'event':self.feeder_event,
                           'connectivity':True}
                json_message = json.dumps(message)
                #self.state_socket.sendall(json_message.encode('UTF-8'))
                duration = time.time() - s_time
                print('duration of state_event:',duration)
                if self.state_event_period > duration:
                    time.sleep(1 - duration)
                else:
                    print('time over')
                    pass
            except:
                print('error in state_event')
                self.feeder_stop()    
                self.event.set()  
                
        print('state event : 서버와 연결이 끊어졌습니다')
        print('state event terminated!')     
        self.state_socket.close()
        self.init_set()
    
    def cmd_event(self):
        # server로부터 command 수신 #
        while not self.event.is_set():
            try:
                print('test cmd')
                data = self.cmd_socket.recv(self.BUFFER)
                if data:
                    # command에 따른 logic coding
                    print(data)
                    if data.decode() == 'ID':
                        message = {'ID':self.feeder_ID}
                        json_message = json.dumps(message)
                        self.cmd_socket.sendall(json_message.encode('UTF-8'))
                    else:
                        # 메시지 parsing
                        
                        pass
                
                else:
                    print('서버와 연결이 끊어졌습니다')
                    self.event.set()
                    self.feeder_stop()
                    
            except: 
                print('error in cmd_event') 
                self.event.set()
                
        print('cmd event : 서버와 연결이 끊어졌습니다')
        print('cmd event terminated!')
        self.cmd_socket.close()
    
    def control_event(self):
        # 0.1초 loop : 로드셀, pid 제어 진행
        #LC = Loadcell()      
        while not self.isTerminate:
            try:
                feed_mode = self.feed_mode
                ## Load_cell ##
                #s_time = time.time()
                #self.weight=LC.get_weight(8)
                #e_time = time.time()
                #print('elaped time = ', e_time-s_time)  
                
                if feed_mode == 'auto':
                    print('PID 제어')
                elif feed_mode == 'manual':
                    print('manual test')
                elif feed_mode == 'stop':
                    print('stop test')
                    self.feeder_stop()
                else:
                    print('feed mode error')        
            except:
                print('error in control event')
                break
            time.sleep(5)
        print('control event terminated!')
    
    def feeder_stop(self):
        self.feed_motor_pwm = 0
        self.spread_motor_pwm = 0
        self.feed_mode = 'stop'

if __name__ == "__main__":
    server_ip = '127.0.0.1' # server ip
    Feeder_01 = Feeder_client(server_ip,2200,2201)
    try:
        while True:
            #print('test 중')
            time.sleep(1)
    except KeyboardInterrupt:
        print('사용자종료')