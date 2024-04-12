import time

info = {"F-01":{"feeder_ID":"F-01","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-02":{"feeder_ID":"F-02","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-03":{"feeder_ID":"F-03","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-04":{"feeder_ID":"F-04","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-05":{"feeder_ID":"F-05","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-06":{"feeder_ID":"F-06","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-07":{"feeder_ID":"F-07","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-08":{"feeder_ID":"F-08","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-09":{"feeder_ID":"F-09","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")},\
        "F-10":{"feeder_ID":"F-10","feed_size":3,"remains":5,"feed_motor_ouput":0,"spread_motor_ouput":0,\
                "feed_mode":"stop","event":{"remains":"enough feed","motor_state":"stop"},\
                "connectivity":False,"time":time.strftime("%y/%m/%d %H:%M:%S")}}

auto_plan = {"F-01":{0:{'start time' : '20:31','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                     1:{'start time' : '20:32','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},\
            "F-02":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-03":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-04":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-05":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-06":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-07":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-08":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},
            "F-09":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}},\
            "F-10":{0:{'start time' : '09:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5},\
                    1:{'start time' : '16:00','pace' : 4.5,'spread':1.5, 'feed amount' : 1.5}}}