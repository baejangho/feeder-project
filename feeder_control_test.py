#!/usr/bin/env python3
import RPi.GPIO as GPIO  # import GPIO
from feeder_pid_module import Pid_control
from feeder_loadcell import Loadcell
from feeder_motor_test import Motor_control
from rpi_hardware_pwm import HardwarePWM
import time

kp = 2
ki = 0.00017
min_pwm = 0
max_pwm = 100

PC = Pid_control(min_pwm,max_pwm,kp,ki,0)
LC = Loadcell()
MT = Motor_control()

try:
    init_weight = LC.get_weight(8)
    desired_vel = 4 # gram/sec
    elapsed_time = 0
    desired_weight = PC.desired_weight_calc(elapsed_time,desired_vel,init_weight)
    total_weight = 200
    distance = 1.5 # m
    pid_state = True
    cur_weight = init_weight
    

    while True:
        if pid_state:
            if cur_weight > (init_weight - total_weight):
                s_time = time.time()
                cur_weight = LC.get_weight(8)
                pwm = PC.calc(elapsed_time, desired_weight, cur_weight)
                MT.supply_motor_pwm(pwm)
                MT.spread_motor_pwm(30)
                e_time = time.time()
                elapsed_time = e_time - s_time
                print('elaped time = ', elapsed_time)
                desired_weight = PC.desired_weight_calc(elapsed_time,desired_vel,desired_weight)
            else:
                init_weight = LC.get_weight(8)
                pid_state = False
        else:
            
        
        
except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

finally:
    MT.terminate()