#!/usr/bin/env python3

class Pid_control:
 
    def __init__(self, _min=0, _max=100, _kp=2, _ki=0.00017, _kd=0):
        self.update(_min, _max, _kp, _ki, _kd)
 
    def update(self, _min, _max, _kp, _ki, _kd):
        self.min = _min
        self.max = _max
        self.kp = _kp
        self.ki = _ki
        self.kd = _kd
        self.pre_error = 0
        self.integral = 0
 
    def calc(self, dt, sv, pv):
        try:
            error = sv - pv
            # 비례
            kp = self.kp * error
<<<<<<< HEAD
    
=======
 
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            # 적분
            self.integral += error * dt
            ki = self.ki * self.integral
    
<<<<<<< HEAD
            # 미분
=======
            # 미분              
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            kd = (error - self.pre_error) / dt
            kd = self.kd * kd
    
            # 합산
            result = -(kp + ki + kd)
<<<<<<< HEAD
    
=======
            
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
            if result > self.max:
                result = self.max
            elif result < self.min:
                result = self.min
            print('pwm result:',result)
            self.pre_error = error
<<<<<<< HEAD
        except:
            result = 0 
        #description
        #desc = f'Kp :\t{kp:.3f}\nKi :\t{ki:.3f}\nKd :\t{kd:.3f}\nPv :\t{pv:.3f}\nSv :\t{sv:.3f}'
=======
    
            #description
            #desc = f'Kp :\t{kp:.3f}\nKi :\t{ki:.3f}\nKd :\t{kd:.3f}\nPv :\t{pv:.3f}\nSv :\t{sv:.3f}'
        except:
            result = 0
            print("pid problem")
>>>>>>> 0f485d4ee6512b869702ceb3eaf98bc8c8068537
 
        return result#, desc
    
    def desired_weight_calc(self, dt, desired_vel, init_weight):
        desired_weight = init_weight - desired_vel*dt
        return desired_weight