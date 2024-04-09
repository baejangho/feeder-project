#!/usr/bin/env python3
import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
import time

class Loadcell:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
        self.hxL = HX711(dout_pin=23, pd_sck_pin=24, gain_channel_A=128, select_channel='A')  # create an object
        self.hxR = HX711(dout_pin=25, pd_sck_pin=26, gain_channel_A=128, select_channel='A')  # create an object
        # 파일에서 offset, scale_ratio 불러오는 코드 추가
        
    def get_offset_LC_L(self):
        # measure tare and save the value as offset for Left Loadcell
        err1 = self.hxL.zero()
        # check if successful
        if err1:
            raise ValueError('Tare of hxA is unsuccessful.')
        return self.hxL.get_current_offset(channel='A',gain_A=128)
    
    def get_offset_LC_R(self):
        # measure tare and save the value as offset for Left Loadcell
        err1 = self.hxR.zero()
        # check if successful
        if err1:
            raise ValueError('Tare of hx1 is unsuccessful.')
        return self.hxR.get_current_offset(channel='A',gain_A=128)
    
    def get_offset(self):
        # measure tare and save the value as offset for All Loadcell
        print('Tare(offset) of Left LC :',self.get_offset_LC_L())
        print('Tare(offset) of Right LC :',self.get_offset_LC_R())
        reading = self.hxL.get_raw_data_mean()
        if reading:  # always check if you get correct value or only False
            # now the value is close to 0
            print('Data subtracted by offset but still not converted to units:',
                reading)
        else:
            print('invalid data', reading)        
            pass

    def get_scale_ratio(self):
        # In order to calculate the conversion ratio to some units, in my case I want grams,
        # you must have known weight.
        print('Put 1Kg weight on the scale')
        for i in range(5):
            print(i,'sec')
            time.sleep(1)
        reading_L = self.hxL.get_data_mean()
        reading_R = self.hxR.get_data_mean()
        if reading_L or reading_R:
            print('Mean value from LC_L subtracted by offset:', reading_L)
            print('Mean value from LC_R subtracted by offset:', reading_R)
            known_weight_grams = 500
            # set scale ratio for particular channel and gain which is
            # used to calculate the conversion to units. Required argument is only
            # scale ratio. Without arguments 'channel' and 'gain_A' it sets
            # the ratio for current channel and gain.
            ratio_L = reading_L / known_weight_grams  # calculate the ratio for channel A and gain 128
            ratio_R = reading_R / known_weight_grams  # calculate the ratio for channel A and gain 128
            self.hxL.set_scale_ratio(ratio_L)  # set ratio for current channel
            self.hxR.set_scale_ratio(ratio_R)  # set ratio for current channel
            print('Ratio is set.')

    def get_weight_L(self, num=20):
        data_L = self.hxL.get_weight_mean(num)
        print(data_L, 'g')
        return data_L
    
    def get_weight_R(self, num=20):
        data_R = self.hxR.get_weight_mean(num)
        print(data_R, 'g')
        return data_R

    def get_weight(self, num=20):
        data_A = self.hxL.get_weight_mean(num)
        data_B = self.hxR.get_weight_mean(num)
        weight = data_A + data_B
        print(weight, 'g')
        return weight

    def terminate(self):
        GPIO.cleanup()

if __name__ == "__main__":
    LC = Loadcell()
    try:
       LC.get_offset()
       LC.get_scale_ratio()
       while True:
           s_time = time.time()
           LC.get_weight(4)
           e_time = time.time()
           print('elaped time = ', e_time-s_time)
    except (KeyboardInterrupt, SystemExit):
        print('Bye :)')

    finally:
        LC.terminate()