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
    import feeder_loadcell
    import feeder_motor

class Feeder_client:
    def __init__(self, ip, state_port=2200, cmd_port=2201):
        ## TCP/IP 설정 ##
        self.ip = ip                                 # server ip
        self.state_port = state_port                 # server state port
        self.cmd_port = cmd_port                     # server cmd port
        self.BUFFER = 2**15                          # buffer max size
        
        ## feeder state parameter 초기화 ##
        self.feeder_ID = 'F-02'
        self.weight = 10.0              # 사료잔량 : kg 단위
        self.feed_size = 3              # 사료 사이즈 : 호
        self.feeding_motor_pwm = 0         # feed motor pwm : 0~100  
        self.spread_motor_pwm = 0       # spread motor pwm : 0~100
        self.weight_event = "enough feed"   # remains_state : enough feed, low feed
        self.motor_event = "stop"           # motor_state : stop, running, over current
        self.feeding_mode = "stop"      # feed mode : "auto", "manual", "stop"
        self.feeding_distance = 0       # 살포 거리 : m 단위
        self.state_event_period = 1     # sec
        self.connectivity = False
        self.feeder_event = {"remains_state":self.weight_event,
                             "motor_state":self.motor_event}
        self.ip_address = "0.0.0.0"
        self.feeder_state_update()
        
        ## PID 제어 parameter ##
        self.control = feeder_pid_module.Pid_control()
        self.feeding_cmd = False
        self.target_weight = 0 # kg
        self.feeding_pace = 0 # kg/min
        self.previous_feed_amount = None
<<<<<<< HEAD
        self.previous_time = None
=======
        self.feed_change_per_second = None
        self.prev_weight = None
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
        
        if sim == False:
            ## loadcell parameter ##
            self.loadcell = feeder_loadcell.Loadcell()
            ## motor parameter ##
            self.motor = feeder_motor.Motor_control()
        
        self.event = threading.Event()
        self.init_set()
    
    def initialize_socket(self):
        try:
            self.event.clear() 
            self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # state socket 생성
            self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # state socket 생성
            self.state_socket.connect((self.ip, self.state_port))                    # server로 연결 요청
            self.ip_address = self.state_socket.getsockname()[0]
            self.cmd_socket.connect((self.ip, self.cmd_port))
            self.cmd_thread()
            self.state_duration = 0
            self.control_duration = 0
            self.state_event()
            self.control_event()
        except:
            print('서버와 연결되지 않았습니다.')
            self.init_set()
    
    def init_set(self):
        print('서버와 접속을 시도합니다')
        self.feeding_motor_pwm = 0
        self.spread_motor_pwm = 0
        time.sleep(2)
        self.initialize_socket() 
        
    def cmd_thread(self):
        cmd_th = threading.Thread(target = self.cmd_event)
        cmd_th.daemon = True
        cmd_th.start() 
    
    def state_event(self):
        # 급이기 정보 server로 전달 #
        s_time = time.time()
        state_timer = None  # state_timer를 None으로 초기화
        
        #print(time.strftime("%y/%m/%d %H:%M:%S"))
        try:
            if sim == False:
<<<<<<< HEAD
                current_feed_amount = round(self.weight * 1000,0) # g 단위
            else:
                current_feed_amount = round(self.weight * 1000,0) # g 단위
=======
                current_feed_amount = round(self.weight * 1000,0)
            else:
                current_feed_amount = round(self.weight * 1000,0)
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            if self.previous_feed_amount is not None and self.previous_time is not None:
                # 이전에 측정한 사료량과 시간과 현재 측정한 사료량과 시간의 차이를 계산합니다.
                time_difference = (s_time - self.previous_time)
                feed_change = current_feed_amount - self.previous_feed_amount
<<<<<<< HEAD
                feed_change_per_second = round(feed_change / time_difference,2)
                print('사료량 변화율:', feed_change_per_second)
=======
                self.feed_change_per_second = round(feed_change / time_difference,2)
                print('사료량 변화율:', self.feed_change_per_second)
            print('current feed amount:',current_feed_amount)
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            # 현재 시간과 사료량을 저장합니다.
            self.previous_time = s_time
            self.previous_feed_amount = current_feed_amount
            
            self.connectivity = True
            state_msg = self.feeder_state_update()
            json_state_msg = json.dumps(state_msg)
            self.state_socket.sendall(json_state_msg.encode('UTF-8'))
            #time.sleep(0.6)
            duration = time.time() - s_time
            # if self.state_event_period > duration:
            #     print('state event duration :', duration)
            # else:
            #     print('time over')
            state_timer = threading.Timer(max(1-duration,0), self.state_event)
            state_timer.daemon = True
            state_timer.start()   
        except Exception as e:
            print('error in state_event:', e)
            self.connectivity = False
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
                data = self.cmd_socket.recv(self.BUFFER) 
                data = json.loads(data)
                print(data)
                if data["type"] == 'ID':
                    cmd = {"type":"ID","cmd":self.feeder_ID,"value":""}
                    json_cmd = json.dumps(cmd)
                    self.cmd_socket.sendall(json_cmd.encode('UTF-8'))
                elif data["type"] == 'set':
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
                        self.init_weight = self.weight
                        self.feeding_amount = data["value"]["feeding_amount"] # kg  
                        self.target_weight = self.init_weight - self.feeding_amount # kg
                        ## 남은 사료량 확인 ##
                        if self.check_feeding_amount(self.target_weight):
                            self.feeder_stop()
                            self.feeding_cmd = False
                        
                        if self.feeding_mode == 'auto':
                            self.feeding_cmd = True
                            self.feeding_pace = data["value"]["feeding_pace"]  # kg/min
                            self.feeding_distance = data["value"]["feeding_distance"]  # m 
                            self.desired_weight = self.init_weight # kg
                            ## feeding start log ##
                            # 코드 작성 필요  
                        else:
                            self.feeding_cmd = False
                            
                            ## feeding 실패 log ##
                            # 코드 작성 필요  
                            
                    ## low feed log ##   
                    elif data["cmd"] == "manual":
                        self.feeding_mode = 'manual'
                        # feeder_state update
                        self.feeder_state_update()
                        self.init_weight = self.weight  # kg
                        self.feeding_amount = data["value"]["feeding_amount"] # kg 
                        self.target_weight = self.init_weight - self.feeding_amount # kg
<<<<<<< HEAD
                        print("target_weight:",self.target_weight)                        
=======
                        print("target weight:",self.target_weight)                        
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
                        ## 남은 사료량 확인 ##
                        if self.check_feeding_amount(self.target_weight):
                            self.feeder_stop()
                            self.feeding_cmd = False
                            # feeder_state update
                            # self.feeder_state_update()   
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
                self.connectivity = False
                self.feeder_stop()
                self.event.set()        
        print('cmd event : 서버와 연결이 끊어졌습니다')
        print('cmd event terminated!')
        self.cmd_socket.close()
    
    def control_event(self):
        ## loop 시작 시간 ##
        s_time = time.time()  
        control_timer = None  # state_timer를 None으로 초기화 
        # 0.1초 loop : 로드셀, pid 제어 진행
        dt = 0.2
        
        try:    
            if sim == False:
                ## Load_cell ##
<<<<<<< HEAD
                self.weight = self.loadcell.get_weight(8)/1000 # kg 단위
=======
                self.weight = self.loadcell.get_weight(4)/1000
                print("real:",self.weight)
                if self.weight == 0:
                    self.weight = self.prev_weight
                if self.prev_weight is not None:
                    if abs(self.prev_weight - self.weight) > 0.2:
                        self.weight = self.prev_weight
                        pass
                        #self.weight = self.prev_weight
                print("after:",self.weight)
                self.prev_weight = self.weight 
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            ## 제어 파라미터 ##
            cur_weight = self.weight * 1000 # g 단위
            target_weight = self.target_weight * 1000 # g 단위
            feeding_cmd = self.feeding_cmd
            feeding_pace = self.feeding_pace * 1000 / 60 # g/s 단위
            ## feeding_mode ##
            feeding_mode = self.feeding_mode
            ## 주기적으로 남은 사료량 확인 ##
            self.check_feed_state(cur_weight)   # g 단위로 check
            
            if (feeding_mode == 'auto' or feeding_mode == "manual") & feeding_cmd == True:
                ## feeding 진행 ##
                if cur_weight > target_weight:     # 목표 사료량 달성 전    
                    desired_weight = self.desired_weight * 1000 # g 단위
                    print('pidtest')
                    feeding_pwm = self.control.calc(dt, desired_weight, cur_weight) # g 단위
                    feeding_pwm = 15
                    spreading_pwm = 20 #self.dist2pwm(self.feed_distance)
                    if sim == True:
                        ## loadcell simulation ##
                        self.weight = self.weight - dt * feeding_pace / 1000   # kg 단위
                    else:
                        ## real operation ##
                        print('motor pwm change')
                        if feeding_pwm == self.feed_motor_pwm:
                            pass
                        else:
                            self.motor.supply_motor_pwm (feeding_pwm)
                            self.motor.spread_motor_pwm(spreading_pwm)
                        
                    ## 현재 motor pwm 업데이트 ##
                    self.feeding_motor_pwm = feeding_pwm
                    self.spread_motor_pwm = spreading_pwm
                    
                    ## PID제어를 위한 다음 desired weight 계산 ##
                    self.desired_weight = self.control.desired_weight_calc(dt, feeding_pace/1000, desired_weight/1000) # kg 단위
                    
                    self.motor_event = "running"
                    self.feeder_event['motor_state'] = self.motor_event
                    self.feeder_state_update()
                    
                else:   # 목표 사료량 달성 후
<<<<<<< HEAD
                    print("feed end")
                    self.feeding_motor_pwm = 0
                    self.spread_motor_pwm = 0
                    self.feeding_cmd = False
                    if sim == False:
                        self.motor.supply_motor_pwm(self.feeding_motor_pwm)
=======
                    print("feeed end")
                    self.feed_motor_pwm = 0
                    self.spread_motor_pwm = 0
                    self.feeding_cmd = False
                    if sim == False:
                        self.motor.supply_motor_pwm(self.feed_motor_pwm)
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
                        self.motor.spread_motor_pwm(self.spread_motor_pwm)
                    self.motor_event = "stop"
                    self.feeder_event['motor_state'] = self.motor_event
                    self.feeder_state_update()
                    ## feeding end log ##
                        # 코드 작성 필요   

            elif feeding_mode == 'stop':
                #print('feeding stop : feed_mode = stop')
                self.feeder_stop()
            else:
                #print('feed mode :',feeding_mode)
                # feeder_state update
                self.feeder_state_update()
                    
            ## loop time 계산 ##
            duration = time.time() - s_time
            if dt > duration:
                #print('control event duration :', duration)
                pass
            else:
                print('time over')
                pass
            control_timer = threading.Timer(max(1-duration,0), self.control_event)
            control_timer.daemon = True
            control_timer.start()
        except Exception as e:
            print('error in control event', e)
            self.feeder_stop()
            self.motor.terminate()
            if control_timer is not None:
                control_timer.cancel()
            print('control event terminated!')  
        
    def feeder_stop(self):
        self.feeding_motor_pwm = 0
        self.spread_motor_pwm = 0
        if sim == False:
<<<<<<< HEAD
            self.motor.supply_motor_pwm(self.feeding_motor_pwm)
            self.motor.spread_motor_pwm(self.spread_motor_pwm)
        self.motor_event = "stop"
        self.feeder_event['motor_state'] = self.motor_event
=======
            self.motor.supply_motor_pwm(self.feed_motor_pwm)
            self.motor.spread_motor_pwm(self.spread_motor_pwm)
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
        self.feeding_mode = 'stop'
        self.feed_cmd = False
        # feeder_state update
        self.motor_event = "stop"
        self.feeder_event['motor_state'] = self.motor_event
        self.feeder_state_update()
    
    def set_feed_size(self, size):
        self.feed_size = size
        # feeder_state update
        self.feeder_state_update()
    
    def set_feeder_id(self, id):
        self.feed_ID = id
        # feeder_state update
        self.feeder_state_update()
        
    def set_feeding_mode(self, mode):
        self.feeding_mode = mode
        # feeder_state update
        self.feeder_state_update()
        
    def check_feeding_amount(self, target_weight):
        if target_weight < 0: 
            self.weight_event = "low feed"
            self.feeder_event['remains_state'] = self.weight_event
            return True
        else:
            self.weight_event = "enough feed"
            self.feeder_event['remains_state'] = self.weight_event
            return False
         
    def check_feed_state(self, weight):
        if weight < 0.5 * 1000: # g 단위로 확인
            self.weight_event = "low feed"
            self.feeder_event['remains_state'] = self.weight_event

    def feeder_state_update(self):
        time_str = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f")
        time_str = time_str[:-5]
        state_msg = {'timestamp':time_str,
                    'feeder_ID':self.feeder_ID,
                    'ip_address':self.ip_address,
                    'feed_size':self.feed_size,
                    'remains':round(self.weight,2),
                    'feed_motor_output':round(self.feeding_motor_pwm,1),
                    'spread_motor_output':round(self.spread_motor_pwm,1),
                    'feeding_mode':self.feeding_mode,
                    'event':self.feeder_event,
                    'connectivity':self.connectivity}
        self.feeder_state = state_msg 
        #print('update')
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
    
    
