# -*- coding: utf-8 -*-

sim = False

import socket
import threading
import json
import time
import feeder_pid_module
import tkinter as tk
import datetime 
if sim == False:
    import motor_loadcell

class Feeder_client:
    def __init__(self, ip, state_port=2200, cmd_port=2201):
        ## TCP/IP 설정 ##
        self.ip = ip                                 # server ip
        self.state_port = state_port                 # server state port
        self.cmd_port = cmd_port                     # server cmd port
        self.BUFFER = 2**15                          # buffer max size
        
        ## feeder state parameter 초기화 ##
        self.state_msg = self.feeder_state_init()
        self.feed_weight = 20.0
        self.state_msg['remains'] = self.feed_weight

        ## PID 제어 parameter ##
        self.control = feeder_pid_module.Pid_control()
        self.feeding_cmd = False
        self.target_weight = 0 # kg
        self.feeding_pace = 0 # kg/min
        self.previous_feed_amount = None
        self.previous_time = None
        self.prev_feed_weight = None
        self.control_loop = False
        self.feeding_distance = 1.5
        
        if sim == False:
            ## motor and loadcell parameter ##
            self.ML = motor_loadcell.Motor_Loadcell()
            
        self.event = threading.Event()
        self.control_thread()
        self.init_set()
        
    def initialize_socket(self):
        try:           
            self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # state socket 생성
            self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # state socket 생성
            self.state_socket.connect((self.ip, self.state_port))                    # server로 연결 요청
            ip_address = self.state_socket.getsockname()[0]
            ## state_msg update ##
            self.state_msg['ip_address'] = ip_address
            self.cmd_socket.connect((self.ip, self.cmd_port))
            self.cmd_thread()
            self.state_duration = 0
            self.control_duration = 0
            self.state_event()
                
        except:
            print('서버와 연결되지 않았습니다.')
            self.init_set()
    
    def init_set(self):
        print('서버와 접속을 시도합니다')
        # self.feeding_motor_pwm = 0
        # self.spread_motor_pwm = 0
        ## state_msg update ##
        # self.state_msg['feeding_motor_output'] = self.feeding_motor_pwm
        # self.state_msg['spread_motor_output'] = self.spread_motor_pwm
        # if sim == False:
        #     self.ML.supply_motor_pwm(self.feeding_motor_pwm)
        #     self.ML.spread_motor_pwm(self.spread_motor_pwm)
        time.sleep(2)
        if not self.control_loop:
            self.control_thread()
        self.initialize_socket() 
        
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
        s_time = time.time()
        state_timer = None  # state_timer를 None으로 초기화
        
        #print(time.strftime("%y/%m/%d %H:%M:%S"))
        try:
            if sim == False:
                current_feed_amount = round(self.feed_weight * 1000,0)
            else:
                current_feed_amount = round(self.feed_weight * 1000,0)
            if self.previous_feed_amount is not None and self.previous_time is not None:
                # 이전에 측정한 사료량과 시간과 현재 측정한 사료량과 시간의 차이를 계산합니다.
                time_difference = (s_time - self.previous_time)
                feed_change = current_feed_amount - self.previous_feed_amount
                self.feed_change_per_second = round(feed_change / time_difference,2)
                #print('사료량 변화율:', self.feed_change_per_second)
            #print('current feed amount:',current_feed_amount)
            # 현재 시간과 사료량을 저장합니다.
            self.previous_time = s_time
            self.previous_feed_amount = current_feed_amount
            
            time_str = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")
            time_str = time_str[:-5]
            ## state_msg update ##
            self.state_msg['timestamp'] = time_str
            self.state_msg['connectivity'] = True
            state_msg = self.state_msg
            
            json_state_msg = json.dumps(state_msg)
            self.state_socket.sendall(json_state_msg.encode('UTF-8'))
            #time.sleep(0.6)
            duration = time.time() - s_time

            state_timer = threading.Timer(max(1-duration,0), self.state_event)
            state_timer.daemon = True
            state_timer.start()   
        except Exception as e:
            print('error in state_event:', e)
            ## state_msg update ##
            self.state_msg['connectivity'] = False
            self.feeder_stop()    
            self.event.set()     
            print('state event : 서버와 연결이 끊어졌습니다')
            print('state event terminated!')
            ## log 작성 필요 ## 
            self.state_socket.close()
            if state_timer is not None:  # state_timer가 None이 아닌지 확인
                state_timer.cancel()
            self.init_set()
    
    def cmd_event(self):
        ## server로부터 command 수신 ##
        while not self.event.is_set():
            try:
                ## command에 따른 logic coding ##
                print('cmd event test')
                data = self.cmd_socket.recv(self.BUFFER)
                print('cmd event test')
                data = json.loads(data)
                print(data)
                if data["type"] == 'set':
                    if data["cmd"] == "size":
                        self.set_feed_size(data["value"])
                    elif data["cmd"] == "id":
                        self.set_feeder_id(data["value"])
                    elif data["cmd"] == "mode":
                        self.set_feeding_mode(data["value"])
                    else:
                        print('set command error')
                elif data["type"] == 'control':
                    if data["cmd"] == "start":
                        self.init_weight = self.feed_weight
                        self.feeding_amount = data["value"]["feeding_amount"] # kg  
                        self.target_weight = self.init_weight - self.feeding_amount # kg
    
                        if self.state_msg['feeding_mode'] == 'auto':
                            self.feeding_cmd = True
                            self.feeding_pace = data["value"]["feeding_pace"]  # kg/min
                            self.feeding_distance = data["value"]["feeding_distance"]  # m 
                            self.desired_weight = self.init_weight # kg
                            ## feeding start log ##
                            # 코드 작성 필요  
                        else:
                            self.feeding_cmd = False
                        
                        ## 남은 사료량 확인 ##
                        if self.check_feeding_amount(self.target_weight):
                            self.feeder_stop()
                            self.feeding_cmd = False
                            
                            ## feeding 실패 log ##
                            # 코드 작성 필요  
                            
                    ## low feed log ##   
                    elif data["cmd"] == "manual":
                        ## state_msg update ##
                        self.state_msg['feeding_mode'] = 'manual'
                        self.init_weight = self.feed_weight  # kg
                        self.feeding_amount = data["value"]["feeding_amount"] # kg 
                        self.target_weight = self.init_weight - self.feeding_amount # kg
                        print("target weight:",self.target_weight)                        
                        ## 남은 사료량 확인 ##
                        if self.check_feeding_amount(self.target_weight):
                            self.feeder_stop()
                            self.feeding_cmd = False

                        else:   # 사료 충분
                            self.feeding_cmd = True
                            self.feeding_pace = data["value"]["feeding_pace"]           # kg/min     
                            self.feeding_distance = data["value"]["feeding_distance"]   # m  
                            self.desired_weight = self.init_weight                      # kg 
                            ## feeding start log ##
                            # 코드 작성 필요
                                                  
                    elif data["cmd"] == "stop":
                        self.feeder_stop()
                        ## feeding stop log ##
                        # 코드 작성 필요
                    else:
                        print('control command error')    
                else:
                    print('command type error')  
            except: 
                print('error in cmd_event')
                ## state_msg update ##
                self.state_msg['connectivity'] = False
                self.feeder_stop()
                self.event.set()        
        print('cmd event : 서버와 연결이 끊어졌습니다')
        print('cmd event terminated!')
        self.cmd_socket.close()
    
    def control_event(self):
        ## loop 시작 시간 ##
        # 0.1초 loop : 로드셀, pid 제어 진행
        dt = 0.2
        duration = 0.1
        while True:
            
            #print('control event')
            s_time = time.time()
            time_str = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")
            time_str = time_str[:-5]
            print('loop time:',time_str)
            # control_timer = None  # state_timer를 None으로 초기화 
            
            
            try:
                self.control_loop = True   # control loop 상태 변경(활성)   
                if sim == False:
                    if self.feeding_cmd == True: 
                        ## Load_cell ##
                        feed_weight = self.ML.get_weight(4)/1000 # kg 단위
                        print("real:",feed_weight)
                        if feed_weight == 0:
                            self.feed_weight = self.prev_feed_weight
                        elif self.prev_feed_weight is not None:
                            if abs(self.prev_feed_weight - feed_weight) > 0.1:
                                self.feed_weight = self.prev_feed_weight
                            else:
                                self.feed_weight = feed_weight
                        else:
                            self.feed_weight = feed_weight
                        print("after:",round(self.feed_weight,3))
                        
                    else:
                        feed_weight = self.ML.get_weight(4)/1000 # kg 단위
                        self.feed_weight = feed_weight
                    ## state_msg update ##
                    self.state_msg['remains'] = round(self.feed_weight,3)
                    self.prev_feed_weight = self.feed_weight
                    
                ## 제어 파라미터 ##
                cur_weight = self.feed_weight * 1000 # g 단위
                target_weight = self.target_weight * 1000 # g 단위
                feeding_cmd = self.feeding_cmd
                feeding_pace = self.feeding_pace * 1000 / 60 # g/s 단위
                feeding_distance = self.feeding_distance
                ## feeding_mode ##
                feeding_mode = self.state_msg['feeding_mode']
                ## 주기적으로 남은 사료량 확인 ##
                self.check_feed_state(cur_weight)   # g 단위로 check
                
                if (feeding_mode == 'auto' or feeding_mode == "manual") & feeding_cmd == True:
                    ## feeding 진행 ##
                    if cur_weight > target_weight:     # 목표 사료량 달성 전    
                        desired_weight = self.desired_weight * 1000 # g 단위
                        #print('pidtest')
                        feeding_pwm = self.control.calc(dt, desired_weight, cur_weight) # g 단위
                        feeding_pwm = 100
                        # spreading_pwm = self.ML.spread_motor_distance2pwm(feeding_distance)
                        spreading_pwm = 0
                        if sim == True:
                            ## loadcell simulation ##
                            self.feed_weight = self.feed_weight - dt * feeding_pace / 1000   # kg 단위
                            ## state_msg update ##
                            self.state_msg['remains'] = round(self.feed_weight,2)
                        else:
                            ## real operation ##
                            print('motor pwm change')
                            if feeding_pwm == self.feeding_motor_pwm:
                                pass
                            else:
                                self.ML.supply_motor_pwm(feeding_pwm)
                                self.ML.spread_motor_pwm(spreading_pwm)
                            
                        ## 현재 motor pwm 업데이트 ##
                        self.feeding_motor_pwm = feeding_pwm
                        self.spread_motor_pwm = spreading_pwm
                        ## state_msg update ##
                        self.state_msg['feeding_motor_output'] = self.feeding_motor_pwm
                        self.state_msg['spread_motor_output'] = self.spread_motor_pwm
                        
                        ## PID제어를 위한 다음 desired weight 계산 ##
                        if abs(self.desired_weight - target_weight) < 0.1:
                            self.desired_weight = target_weight 
                        else:  
                            self.desired_weight = self.control.desired_weight_calc(dt, feeding_pace/1000, desired_weight/1000) # kg 단위
                        print('desired weight:',self.desired_weight)
                        ## state_msg update ##
                        self.state_msg['event']['motor_state'] = 'running'
                        
                    else:   # 목표 사료량 달성 후
                        print("feeed end")
                        self.feeding_motor_pwm = 0
                        self.spread_motor_pwm = 0
                        ## state_msg update ##
                        self.state_msg['feeding_motor_output'] = self.feeding_motor_pwm
                        self.state_msg['spread_motor_output'] = self.spread_motor_pwm
                        self.feeding_cmd = False
                        if sim == False:
                            self.ML.supply_motor_pwm(self.feeding_motor_pwm)
                            self.ML.spread_motor_pwm(self.spread_motor_pwm)
                        ## state_msg update ##
                        self.state_msg['event']['motor_state'] = 'stop'
                        ## feeding end log ##
                            # 코드 작성 필요   

                elif feeding_mode == 'stop':
                    #print('feeding stop : feed_mode = stop')
                    self.feeder_stop()
                else:
                    pass
                        
                ## loop time 계산 ##
                duration = time.time() - s_time
                print('duration',duration)
                if dt > duration:
                    print('control event duration :', duration)
                    time.sleep((dt-duration))
                    pass
                else:
                    print('time over')
                    pass
                # control_timer = threading.Timer(max((dt-duration),0.01), self.control_event)
                # control_timer.daemon = True
                # control_timer.start()
                # print('timer start')
         
            
            
            except Exception as e:
                self.control_loop = False   # control loop 상태 변경(비활성)
                print('error in control event', e)
                self.feeder_stop()
                if sim == False:
                    self.ML.terminate()
                # if control_timer is not None:
                #     control_timer.cancel()
                print('control event terminated!')  
            
    def feeder_stop(self):
        self.feeding_motor_pwm = 0
        self.spread_motor_pwm = 0
        ## state_msg update ##
        self.state_msg['feeding_motor_output'] = self.feeding_motor_pwm
        self.state_msg['spread_motor_output'] = self.spread_motor_pwm
        if sim == False:
            self.ML.supply_motor_pwm(self.feeding_motor_pwm)
            self.ML.spread_motor_pwm(self.spread_motor_pwm)
        self.feed_cmd = False
        ## state_msg update ##
        self.state_msg['event']['motor_state'] = 'stop'
        self.state_msg['feeding_mode'] = 'stop'
    
    def set_feed_size(self, size):
        ## state_msg update ##
        self.state_msg['feed_size'] = size
    
    def set_feeder_id(self, id):
        ## state_msg update ##
        self.state_msg['feeder_ID'] = id
        
    def set_feeding_mode(self, mode):
        ## state_msg update ##
        self.state_msg['feeding_mode'] = mode

    def check_feeding_amount(self, target_weight):
        if target_weight < 0: 
            ## state_msg update ##
            self.state_msg['event']['remains_state'] = "low feed"
            return True
        else:
            ## state_msg update ##
            self.state_msg['event']['remains_state'] = "enough feed"
            return False
         
    def check_feed_state(self, weight):
        if weight < 0.5 * 1000: # g 단위로 확인
            ## state_msg update ##
            self.state_msg['event']['remains_state'] = "low feed"
    
    def feeder_state_init(self):
        time_str = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")
        time_str = time_str[:-5]
        state_msg = {'timestamp':time_str,
                    'feeder_ID':'F-01',
                    'ip_address':'0.0.0.0',
                    'feed_size':3,
                    'remains':10.0,
                    'feeding_motor_output':0,
                    'spread_motor_output':0,
                    'feeding_mode':'stop',
                    'event':{"remains_state":"",
                             "motor_state":'stop'},
                    'connectivity': True}
        return  state_msg

if __name__ == "__main__":
    server_ip = '127.0.0.1' # server ip
    Feeder_01 = Feeder_client(server_ip,2200,2201)
    while True:
        try:
            time.sleep(1)
            #print(Feeder_01.feeder_state)
        except KeyboardInterrupt:
            print('사용자종료')
            break
# UI를 실행합니다.
    
    
