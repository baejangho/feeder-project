import feeder_server
import tkinter as tk

def function1():
    print(FS.get_feeder_info('F-01'))
    print("Function 1 is executed!")

def function2():
    print(FS.get_feeder_state_all())
    print("Function 2 is executed!")

def function3():
    print(FS.set_feeding_mode("stop","F-01"))
    print("Function 3 is executed!")
    

root = tk.Tk()

button1 = tk.Button(root, text="Execute Function 1", command=function1)
button1.grid(row=0, column=0)

button2 = tk.Button(root, text="Execute Function 2", command=function2)
button2.grid(row=0, column=1)

button3 = tk.Button(root, text="Execute Function 3", command=function3)
button3.grid(row=1, column=0)

info = {"key1": "value1", "key2": "value2", "key3": "value3"}

info_label = tk.Label(root, text=str(info))
info_label.grid(row=2, column=0, columnspan=2)

server_ip = '127.0.0.1'
state_port = 2200
cmd_port = 2201
FS = feeder_server.Feeder_server(server_ip, state_port, cmd_port)
root.mainloop()