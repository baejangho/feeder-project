#!/usr/bin/env python3
import RPi.GPIO as GPIO  # import GPIO
from rpi_hardware_pwm import HardwarePWM
import time
import numpy as np

class Motor_control:
    def __init__(self):
        #GPIO.cleanup()
        #GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
        GPIO.setup(5, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.HIGH)
        self.pwm1 = HardwarePWM(pwm_channel=0, hz=1_000)
        self.pwm2 = HardwarePWM(pwm_channel=1, hz=1_000)
        self.pwm1.start(0)
        self.pwm2.start(0)
        
    def supply_motor_pwm(self, pwm):
        self.pwm1.change_duty_cycle(pwm)
        
    def spread_motor_pwm(self, pwm):
        self.pwm2.change_duty_cycle(pwm)
        
    def spread_motor_dist(self, dist):
        pwm = self.spread_modtor_distance2pwm(dist)
        self.pwm2.change_duty_cycle(pwm)
    
    def spread_motor_distance2pwm(self, dist: float):
        dist_values = np.array([0.7, 1.1, 1.4, 1.8, 2.4, 2.8])
        pwm_values = np.array([20, 30, 40, 50, 60, 70])

        if dist < dist_values[0]:
            dist = dist_values[0]
            print("최소 거리는 0.7 m 입니다.")
        if dist > dist_values[-1]:
            dist = dist_values[-1]
            print("최대 거리는 2.8 m 입니다.")

        pwm = np.interp(dist, dist_values, pwm_values)
        return pwm

    def terminate(self):
        print("Cleaning...")
        self.pwm1.change_duty_cycle(0)
        self.pwm2.change_duty_cycle(0)
        self.pwm1.stop()
        self.pwm2.stop()
        print("Bye!")
        GPIO.cleanup()

if __name__ == "__main__":
    MT = Motor_control()
    try:
        #MT.supply_motor_pwm(20)
        MT.supply_motor_pwm(100)
        MT.spread_motor_pwm(0)
        time.sleep(10)
        MT.spread_motor_pwm(0)
        MT.supply_motor_pwm(0)

    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
        MT.terminate()