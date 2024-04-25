#!/usr/bin/env python3
import RPi.GPIO as GPIO  # import GPIO
from rpi_hardware_pwm import HardwarePWM
import time

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
        if dist < 0.7:
            dist = 0.7
            print("최소 거리는 0.3 m 입니다.")
        if dist > 2.5:
            dist = 2.5
            print("최대 거리는 4.5 m 입니다.")
        pwm = 60 * dist - 170
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