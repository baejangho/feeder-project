#!/usr/bin/env python3
import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
import time
import json

class Loadcell:
    def __init__(self):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
        self.hx = HX711(dout_pin=23, pd_sck_pin=22, gain_channel_A=128, select_channel='A')  # create an object
        self.load_settings()  # 설정 불러오기      
        
    def set_offset_LC(self):
        # measure  tare and save the value as offset for Left Loadcell
        # 사료를 비운 후 동작해야 함(영점 세팅)
        err = self.hx.zero()
        # check if successful
        if err:
            raise ValueError('Tare of hxA is unsuccessful.')
        reading = self.hx.get_raw_data_mean()
        if reading:  # always check if you get correct value or only False
            # now the value is close to 0
            print('Data subtracted by offset but still not converted to units:',
                reading)
        else:
            print('invalid data', reading)        
            pass
        #파일에 재저장
        self.save_settings()
        return self.hx.get_current_offset(channel='A',gain_A=128)
    
    def get_offset_LC(self):
        # measure tare and save the value as offset for All Loadcell
        print('Tare(offset) of Loadcell :',self.hx.get_current_offset(channel='A',gain_A=128))
        return self.hx.get_current_offset(channel='A',gain_A=128)
        
    def set_scale_ratio_LC(self):
        # In order to calculate the conversion ratio to some units, in my case I want grams,
        # you must have known weight.
        print('Put 1000g weight on the scale')
        for i in range(10):
            print(i,'sec')
            time.sleep(1)
        reading = self.hx.get_data_mean()
        if reading:
            print('Mean value from loadcell subtracted by offset:', reading)
            known_weight_grams = 1000
            # set scale ratio for particular channel and gain which is
            # used to calculate the conversion to units. Required argument is only
            # scale ratio. Without arguments 'channel' and 'gain_A' it sets
            # the ratio for current channel and gain.
            self.ratio = reading / known_weight_grams  # calculate the ratio for channel A and gain 128
            self.hx.set_scale_ratio(self.ratio)  # set ratio for current channel
            print('Ratio is set.:', self.ratio)
        #파일에 업데이트
        self.save_settings()  # 변경사항 저장
        return self.hx.get_current_scale_ratio(channel='A',gain_A=128)
        
    def save_settings(self):
        calibration= {
            'offset': self.hx.get_current_offset(channel='A', gain_A=128),
            'ratio': self.hx.get_current_scale_ratio(channel='A', gain_A=128)
        }
        with open('calibration.json', 'w') as f:
            json.dump(calibration, f, indent="\t")
        print("Settings saved to calibration.json")

    def load_settings(self):
        try:
            with open('calibration.json', 'r') as f:
                calibration= json.load(f)
            self.hx.set_offset(calibration['offset'])
            self.hx.set_scale_ratio(calibration['ratio'])
            print("Settings loaded from calibration.json")
        except FileNotFoundError:
            print("Settings file not found. Using default settings.")    

    def get_weight(self, num=20):
        data = self.hx.get_weight_mean(num)
        #print(data, 'g')
        return data
    
    def terminate(self):
        GPIO.cleanup()

if __name__ == "__main__":
    LC = Loadcell()
    try:
       #LC.set_offset_LC() 
       #LC.get_offset_LC()
       #LC.set_scale_ratio_LC()
       while True:
           s_time = time.time()
           LC.get_weight(8)
           e_time = time.time()
           print('elaped time = ', e_time-s_time)
    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
            
        LC.terminate()
