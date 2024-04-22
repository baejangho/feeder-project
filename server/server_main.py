import tkinter as tk
from feeder_server import Feeder_server
import ast

# Feeder_client 객체를 생성합니다.
server_ip = '127.0.0.1' # server ip
#server_ip = '192.168.0.4'
server = Feeder_server(server_ip,2200,2201)

# Tk 객체를 생성합니다.
root = tk.Tk()

# Frame 객체를 생성합니다.
info_frame = tk.Frame(root)
info_frame.grid(row=0, column=0)
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0)

# state_msg 딕셔너리의 각 키에 대해 StringVar 객체와 Label 위젯을 생성합니다.
label_vars = {}
for i, key in enumerate(server.info.keys()):
    label_var = tk.StringVar()
    label_vars[key] = label_var

    key_label = tk.Label(info_frame, text=key)
    key_label.grid(row=i, column=0)

    value_label = tk.Label(info_frame, textvariable=label_var)
    value_label.grid(row=i, column=1)


def update_labels():
    # state_msg 딕셔너리의 각 키-값 쌍에 대해 StringVar 객체의 값을 업데이트합니다.
    #print(Feeder_01.feeder_state)
    for key, value in server.info.items():
        label_vars[key].set(value)
    # 200ms 후에 이 함수를 다시 호출합니다.
    root.after(200, update_labels)

manual_feeding_plan_entry = tk.Entry(button_frame)
manual_feeding_plan_entry.insert(0, "(20,1.5,1)")
manual_feeding_plan_entry.grid(row=len(label_vars), column=0)
auto_feeding_plan_entry = tk.Entry(button_frame)
auto_feeding_plan_entry.grid(row=len(label_vars)+1, column=0)
print((manual_feeding_plan_entry.get()))

feeder_ids = ['F-01','F-02','F-03','F-04','F-05','F-06','F-07','F-08','F-09','F-10']
selected_feeder_id = tk.StringVar()
selected_feeder_id.set(feeder_ids[0])  # 기본값을 설정합니다.
feeder_id_menu = tk.OptionMenu(button_frame, selected_feeder_id, *feeder_ids)
feeder_id_menu.grid(row=len(label_vars), column=1)
mode_ids = ['auto', 'manual', 'stop']
selected_mode_id = tk.StringVar()
selected_mode_id.set(mode_ids[2])
mode_id_menu = tk.OptionMenu(button_frame, selected_mode_id, *mode_ids)
mode_id_menu.grid(row=len(label_vars)+1, column=1)
feed_size_ids = [3, 4, 5, 6]
selected_feed_size_ids = tk.StringVar()
selected_feed_size_ids.set(feed_size_ids[0])
feed_size_ids_menu = tk.OptionMenu(button_frame, selected_feed_size_ids, *feed_size_ids)
feed_size_ids_menu.grid(row=len(label_vars)+1, column=2)

control_function_dict = {
    'stop_feeding': lambda: server.stop_feeding(selected_feeder_id.get()),
    'stop_feeding_all': server.stop_feeding_all,
    'manual_feeding': (lambda: server.manual_feeding(ast.literal_eval(manual_feeding_plan_entry.get())[0], ast.literal_eval(manual_feeding_plan_entry.get())[1], ast.literal_eval(manual_feeding_plan_entry.get())[2], selected_feeder_id.get())),
    'manual_feeding_all': lambda: server.manual_feeding_all(manual_feeding_plan_entry.get())}
selected_feeder_dict = {
    'set_feeding_mode': lambda: server.set_feeding_mode(selected_mode_id.get(),selected_feeder_id.get()),  # 'mode'는 실제 모드로 변경해야 합니다.
    'set_feeding_mode_all': server.set_feeding_mode_all,
    'set_feeding_plan': lambda: server.set_feeding_plan(auto_feeding_plan_entry.get(),selected_feeder_id.get()),
    'set_feeding_plan_all': lambda: server.set_feeding_plan_all(auto_feeding_plan_entry.get()),
    'set_feed_size': lambda: server.set_feed_size(selected_feed_size_ids.get(), selected_feeder_id.get())} 

# 각 함수에 대해 버튼을 생성합니다.
for i, (button_text, button_function) in enumerate(control_function_dict.items()):
    button = tk.Button(button_frame, text=button_text, command=button_function)
    button.grid(row=len(label_vars), column=i+2)

for i, (button_text, button_function) in enumerate(selected_feeder_dict.items()):
    button = tk.Button(button_frame, text=button_text, command=button_function)
    button.grid(row=len(label_vars)+1, column=i+3)



# UI를 실행합니다.
try:
    update_labels()
    root.mainloop()
except KeyboardInterrupt:
        print('사용자종료')
        root.destroy()