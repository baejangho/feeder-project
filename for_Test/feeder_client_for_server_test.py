# -*- coding: utf-8 -*-

import socket
import threading
import json
import time
import feeder_pid_module
import feeder_loadcell 
import feeder_motor

class Feeder_client:
    def __init__(self, ip, state_port=2200, cmd_port=2201):
        ## TCP/IP 설정 ##
        self.ip = ip                                 # server ip
        self.state_port = state_port                 # server state port
        self.cmd_port = cmd_port                     # server cmd port
        self.BUFFER = 10240                          # buffer max size
        
        ## feeder state parameter 초기화 ##
        self.feeder_ID = 'F-01'
        self.weight = 4.0           # 사료잔량 : kg 단위
        self.feed_size = 3          # 사료 사이즈 : 호
        self.feed_motor_pwm = 0     # feed motor pwm : 0~100  
        self.spread_motor_pwm = 0   # spread motor pwm : 0~100
        self.feeder_event = 'nothing'
        self.feeding_mode = 'stop'     # feed mode : `auto`, `manual`, `stop`
        self.feeding_distance = 0   # 살포 거리 : m 단위
        
        self.isTerminate = False
        self.state_event_period = 1 # sec
        
        ## PID 제어 parameter ##
        self.control = feeder_pid_module.Pid_control()
        self.feeding_cmd = False
        
        ## loadcell parameter ##
        self.LC = feeder_loadcell.Loadcell()
        ## motor parameter ##
        self.MT = feeder_motor.Motor_control()
        
        self.event = threading.Event()
        self.init_set()
        
        self.sim = True 
    
    def initialize_socket(self):
        try:
            self.event.clear() 
            self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # state socket 생성
            self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # state socket 생성
            self.state_socket.connect((self.ip, self.state_port))                    # server로 연결 요청
            self.cmd_socket.connect((self.ip, self.cmd_port))
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
                           'feeding_mode':self.feeding_mode,
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
                        if True:        # auto mode & feeding start cmd
                            self.init_weight = self.weight
                            self.feeding_weight = 1.0    # 메시지에서 받아올 것
                            self.target_weight = self.init_weight - self.feed_weight
                            self.feeding_mode = 'auto'
                            self.feeding_cmd = True
                            self.feeding_pace = 20         # 메시지에서 받아올 것
                            self.feeding_distance = 1.5    # 메시지에서 받아올 것
                            self.desired_weight = self.control.desired_weight_calc(0,self.feed_pace,self.init_weight)
                            ## feeding start log ##
                            # 코드 작성 필요
          
                
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
        duration = 0
          
        while not self.isTerminate:
            try:
                ## loop 시작 시간 ##
                s_time = time.time()
                
                ## feeding_mode ##
                feeding_mode = self.feeding_mode
                
                ## Load_cell ##
                #self.weight = self.LC.get_weight(8)
                cur_weight = self.weight
                
                if (feeding_mode == 'auto' or feeding_mode == "manual") & self.feeding_cmd == True:
                    if cur_weight > self.target_weight:     # feeding 진행
                        print('PID 제어 : feeding 진행 중')
                        desired_weight = self.desired_weight
                        
                        feeding_pwm = self.control.calc(self.elapsed_time, desired_weight, cur_weight)
                        spreading_pwm = 30 #self.dist2pwm(self.feed_distance)
                        
                        if self.sim == True:
                            ## simulation ##
                            print('로드셀 시뮬레이션')
                            self.weight = self.weight - duration * self.feeding_pace
                        else:
                            ## real operation ##
                            self.MT.supply_motor_pwm(feeding_pwm)
                            self.MT.spread_motor_pwm(spreading_pwm)
                         
                        ## 현재 motor pwm 업데이트 ##
                        self.feed_motor_pwm = feeding_pwm
                        self.spread_motor_pwm = spreading_pwm
                        
                        ## PID제어를 위한 다음 desired weight 계산 ##
                        self.desired_weight = self.control.desired_weight_calc(duration, self.feeding_pace, desired_weight)
                        
                    else:   # feeding 종료
                        self.feed_motor_pwm = 0
                        self.spread_motor_pwm = 0
                        self.feed_cmd = False
                        ## feeding end log ##
                            # 코드 작성 필요   

                elif feeding_mode == 'stop':
                    print('feeding stop : feed_mode = stop')
                    self.feeder_stop()
                else:
                    print('feed mode error')
                        
                ## loop time 계산 ##
                duration = time.time() - s_time
                print('duration of state_event:',duration)
                if self.state_event_period > duration:
                    time.sleep(1 - duration)
                else:
                    print('time over')
                    pass    
            except:
                print('error in control event')
                break
            time.sleep(5)
        print('control event terminated!')
    
    def feeder_stop(self):
        self.feed_motor_pwm = 0
        self.spread_motor_pwm = 0
        self.feeding_mode = 'stop'
    
    def set_feed_size(self, size):
        self.feed_size = size

if __name__ == "__main__":
    server_ip = '127.0.0.1' # server ip
    Feeder_01 = Feeder_client(server_ip,2200,2201)
    try:
        while True:
            #print('test 중')
            time.sleep(1)
    except KeyboardInterrupt:
        print('사용자종료')