import time

info = {"F-01":{'timestamp':'00:00:00',"feeder_ID":"F-01",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-02":{'timestamp':'00:00:00',"feeder_ID":"F-02",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-03":{'timestamp':'00:00:00',"feeder_ID":"F-03",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-04":{'timestamp':'00:00:00',"feeder_ID":"F-04",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-05":{'timestamp':'00:00:00',"feeder_ID":"F-05",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-06":{'timestamp':'00:00:00',"feeder_ID":"F-06",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-07":{'timestamp':'00:00:00',"feeder_ID":"F-07",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-08":{'timestamp':'00:00:00',"feeder_ID":"F-08",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-09":{'timestamp':'00:00:00',"feeder_ID":"F-09",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False,},
        "F-10":{'timestamp':'00:00:00',"feeder_ID":"F-10",'ip_address':'0.0.0.0',"feed_size":3,"remains":5,
                "feed_motor_ouput":0,"spread_motor_ouput":0,"feed_mode":"stop",
                "event":{"remains":"enough feed","motor_state":"stop"},"connectivity":False}}

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