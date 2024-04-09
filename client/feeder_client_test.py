import socket
import threading
import json
import time
#from feeder_loadcell_test import Loadcell

class Feeder_client:
    def __init__(self, ip, state_port=2200, cmd_port=2201):
        self.event = threading.Event()
        self.ip = "192.168.0.4"                                                     # server ip
        self.state_port = state_port                                                # server port
        self.cmd_port = cmd_port                                                    # server port
        self.BUFFER = 10240                                                         # buffer max size
        self.feeder_ID = 'F-01'
        self.weight = 0
        self.size = 3
        self.feed_motor_pwm = 0
        self.pread_motor_pwm = 0
        self.isTerminate = False
        self.feed_mode = 'manual'
        self.period_state = 1 # sec
        self.initialize_socket() 
    
    def initialize_socket(self):
        self.event.clear() 
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # state socket 생성
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # state socket 생성
        self.state_socket.connect((self.ip, self.state_port))                       # server로 연결 요청
        self.cmd_socket.connect((self.ip, self.cmd_port))                           # server로 연결 요청 
        self.state_thread()
        self.cmd_thread()
        self.control_thread()
    
    def init_set(self):
        print('서버와 재접속을 시도합니다')
        self.feed_motor_pwm = 0
        self.pread_motor_pwm = 0
        time.sleep(3)
        self.initialize_socket() 

    def state_thread(self):
        state_th = threading.Thread(target = self.state_event)
        #state_th.daemon = True
        state_th.start()
        
    def cmd_thread(self):
        cmd_th = threading.Thread(target = self.cmd_event)
        #cmd_th.daemon = True
        cmd_th.start()
    
    def control_thread(self):
        cmd_th = threading.Thread(target = self.control_event)
        #cmd_th.daemon = True
        cmd_th.start()        
    
    def state_event(self):
        # 급이기 정보 server로 전달 #
        while not self.event.is_set():
            try:
                s_time = time.time()
                print('send state')
                message = {'feeder_ID':self.feeder_ID,
                           'size':self.size,
                           'weight':self.weight,
                           'feed_motor_output':self.feed_motor_pwm,
                           'spread_motor_output':self.pread_motor_pwm,
                           'motor_state':'Good','feed_mode':self.feed_mode,
                           'connectivity':True}
                json_message = json.dumps(message)
                self.state_socket.sendall(json_message.encode('UTF-8'))
                f_time = time.time()
                
                if self.period_state > (f_time - s_time):
                    time.sleep(1 - (f_time - s_time))
                else:
                    print('time over')
                    pass
            except:
                print('error in state_event')    
                self.event.set()  
                break
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
                        message = {'ID':self.feeder_ID}
                        json_message = json.dumps(message)
                        self.cmd_socket.sendall(json_message.encode('UTF-8'))
                
                else:
                    print('서버와 연결이 끊어졌습니다')
                    break
            except: 
                print('error in cmd_event') 
                self.event.set()
                break
        print('cmd event : 서버와 연결이 끊어졌습니다')
        print('cmd event terminated!')
        self.cmd_socket.close()
    
    def control_event(self):
        # 0.1초 loop : 로드셀, pid 제어 진행
        #LC = Loadcell()      
        while not self.isTerminate:
            try:
                feed_mode = self.feed_mode
                ############Load_cell################
                #s_time = time.time()
                #self.weight=LC.get_weight(8)
                #e_time = time.time()
                #print('elaped time = ', e_time-s_time)  
                ############Load_cell#################
                if feed_mode == 'auto':
                    print('auto test')
                elif feed_mode == 'manual':
                    print('manual test')
                elif feed_mode == 'semi_auto':
                    print('semi_auto test')
                else:
                    print('feed mode error')        
            except:
                print('error in control event')
                break
            time.sleep(5)
        print('control event terminated!')

if __name__ == "__main__":
    server_ip = '192.168.0.4' # server ip
    Feeder_01 = Feeder_client(server_ip,2200,2201)