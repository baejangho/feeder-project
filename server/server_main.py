import tkinter as tk
from feeder_server import Feeder_server
import ast

# Feeder_client 객체를 생성합니다.
server_ip = '127.0.0.1' # server ip
#server_ip = '192.168.0.4'
server = Feeder_server(server_ip,2200,2201)

# Tk 객체를 생성합니다.
root = tk.Tk()

# info Frame 객체를 생성
info_frame = tk.Frame(root, borderwidth=2, relief='groove', width=1500, height=150)
info_frame.grid(row=0, column=0)
info_frame.grid_propagate(False)
# info 프레임에 제목 label 추가
info_ID_label = tk.Label(info_frame, text='ID', font=('Arial', 17))
info_ID_label.grid(row=0, column=0,sticky='n')
info_Info_label = tk.Label(info_frame, text='Information', font=('Arial', 17))
info_Info_label.grid(row=0, column=1,sticky='n')

# main1 Frame 객체를 생성
main_frame1 = tk.Frame(root, borderwidth=2, relief='groove', width=1500, height=150)#, width=500, height=300)
main_frame1.grid(row=1, column=0)
main_frame1.grid_propagate(False)
# main2 Frame 객체를 생성
main_frame2 = tk.Frame(root, borderwidth=2, relief='groove', width=1500, height=200)#, width=500, height=300)
main_frame2.grid(row=2, column=0)
main_frame2.grid_propagate(False)

## main1 Frame에 F01, F02, F03 Frame 객체를 생성
## F-01 프레임
F01_frame = tk.Frame(main_frame1, borderwidth=2, relief='groove', width=375, height=150)
F01_frame.grid(row=0, column=0,sticky='n')
F01_frame.grid_propagate(False)
## F-01 프레임에 제목 label 추가
F01_frame_label = tk.Label(F01_frame, text='F-01', font=('Arial', 17))
F01_frame_label.grid(row=0, column=0,sticky='s')
## F-02 프레임
F02_frame = tk.Frame(main_frame1, borderwidth=2, relief='groove', width=375, height=150)
F02_frame.grid(row=0, column=1,sticky='n')
F02_frame.grid_propagate(False)
## F-02 프레임에 제목 label 추가
F02_frame_label = tk.Label(F02_frame, text='F-02', font=('Arial', 17))
F02_frame_label.grid(row=0, column=0,sticky='s')
## F-03 프레임
F03_frame = tk.Frame(main_frame1, borderwidth=2, relief='groove', width=375, height=150)
F03_frame.grid(row=0, column=2,sticky='n')
F03_frame.grid_propagate(False)
## F-03 프레임에 제목 label 추가
F03_frame_label = tk.Label(F03_frame, text='F-03', font=('Arial', 17))
F03_frame_label.grid(row=0, column=0,sticky='s')
## 현황판 프레임
Status_frame = tk.Frame(main_frame1, borderwidth=2, relief='groove', width=375, height=150)
Status_frame.grid(row=0, column=3,sticky='n')
Status_frame.grid_propagate(False)
## F-03 프레임에 제목 label 추가
Status_frame_label = tk.Label(Status_frame, text='Status board', font=('Arial', 17))
Status_frame_label.grid(row=0, column=0,sticky='s')

## main2 frame에 Total, Plan, Setting, Control Frame 객체를 생성
## Total 프레임
Total_frame = tk.Frame(main_frame2, borderwidth=2, relief='groove', width=375, height=200)
Total_frame.grid(row=0, column=0,sticky='n')
Total_frame.grid_propagate(False)
## Total 프레임에 제목 label 추가
Total_frame_label = tk.Label(Total_frame, text='Total plan list', font=('Arial', 17))
Total_frame_label.grid(row=0, column=0,sticky='s')
## Plan 프레임
plan_frame = tk.Frame(main_frame2, borderwidth=2, relief='groove', width=375, height=200)
plan_frame.grid(row=0, column=1,sticky='n')
plan_frame.grid_propagate(False)
## Plan 프레임에 제목 label 추가
plan_frame_label = tk.Label(plan_frame, text='Auto plan', font=('Arial', 17))
plan_frame_label.grid(row=0, column=0)
## Set 프레임
set_frame = tk.Frame(main_frame2, borderwidth=2, relief='groove', width=375, height=200)
set_frame.grid(row=0, column=2,sticky='n')
set_frame.grid_propagate(False)
## Set 프레임에 제목 label 추가
set_frame_label = tk.Label(set_frame, text='Setting', font=('Arial', 17))
set_frame_label.grid(row=0, column=0,sticky='s')
## Control 프레임
control_frame = tk.Frame(main_frame2, borderwidth=2, relief='groove', width=500, height=200)
control_frame.grid(row=0, column=3,sticky='n')
control_frame.grid_propagate(False)
## Control 프레임에 제목 label 추가
control_frame_label = tk.Label(control_frame, text='Control', font=('Arial', 17))
control_frame_label.grid(row=0, column=0,sticky='s')

##########################################################################################
## info 프레임에 전체 급이기 정보 추가
# state_msg 딕셔너리의 각 키에 대해 StringVar 객체와 Label 위젯을 생성합니다.
label_vars = {}
for i, key in enumerate(server.get_feeder_info_all().keys()):
    label_var = tk.StringVar()
    label_vars[key] = label_var

    key_label = tk.Label(info_frame, text=key)
    key_label.grid(row=i+1, column=0)

    value_label = tk.Label(info_frame, textvariable=label_var)
    value_label.grid(row=i+1, column=1)

## info 프레임에 전체 급이기 정보 업데이트
def update_labels():
    # state_msg 딕셔너리의 각 키-값 쌍에 대해 StringVar 객체의 값을 업데이트합니다.
    #print(Feeder_01.feeder_state)
    for key, value in server.get_feeder_info_all().items():
        label_vars[key].set(value)
    # 초당 속도 측정(g/s)
    # 200ms 후에 이 함수를 다시 호출합니다.
    root.after(200, update_labels)

feeder_ids = ['F-01','F-02','F-03','F-04','F-05','F-06','F-07','F-08','F-09','F-10']
## Control 프레임에 내용 추가
# 수동급이 계획 입력창
manual_feeding_plan_label1 = tk.Label(control_frame, text='Manual Plan', font=('Arial', 10))
manual_feeding_plan_label1.grid(row=1, column=0,sticky='n')
manual_feeding_plan_label2 = tk.Label(control_frame, text='(pace, distance, amount)', font=('Arial', 10))
manual_feeding_plan_label2.grid(row=2, column=0,sticky='n')
manual_feeding_plan_entry = tk.Entry(control_frame)
manual_feeding_plan_entry.insert(0, "(20,1.5,1)")
manual_feeding_plan_entry.grid(row=1, column=1)

## Plan 프레임에 내용 추가
# 자동급이 계획 입력창
auto_feeding_plan_label = tk.Label(plan_frame, text='Auto plan', font=('Arial', 10))
auto_feeding_plan_label.grid(row=1, column=0)
auto_feeding_plan_entry = tk.Entry(plan_frame)
auto_feeding_plan_entry.insert(0, "{0:{'start time' : '09:00','pace' : 50,'spread':1.5, 'feed amount' : 1.5},1:{'start time' : '16:00','pace' : 0,'spread':1.5, 'feed amount' : 1.5}}")
auto_feeding_plan_entry.grid(row=2, column=0)
auto_feeding_plan_all_label = tk.Label(plan_frame, text='Auto plan all', font=('Arial', 10))
auto_feeding_plan_all_label.grid(row=1, column=1)
auto_feeding_plan_all_entry = tk.Entry(plan_frame)
auto_feeding_plan_all_entry.grid(row=2, column=1)

auto_feeder_id = tk.StringVar()
auto_feeder_id.set(feeder_ids[0])  # 기본값을 설정합니다.
auto_feeder_id_menu = tk.OptionMenu(plan_frame, auto_feeder_id, *feeder_ids)
auto_feeder_id_menu.grid(row=3, column=0)

def auto_feeding():
    server.set_feeding_plan(ast.literal_eval(auto_feeding_plan_entry.get()),auto_feeder_id.get())
    server.set_feeding_mode('auto',auto_feeder_id.get())

button = tk.Button(plan_frame, text='Auto feeding', command=auto_feeding)
button.grid(row=4, column=0)

## Set 프레임에 내용 추가
# 급이기 선택, 모드 선택, 사료 선택 등
setting_widget_label0 = tk.Label(set_frame, text='feeder select', font=('Arial', 10))
setting_widget_label0.grid(row=1, column=0,sticky='n')
setting_widget_label1 = tk.Label(set_frame, text='mode setting', font=('Arial', 10))
setting_widget_label1.grid(row=1, column=1,sticky='n')
setting_widget_label2 = tk.Label(set_frame, text='feed size setting', font=('Arial', 10))
setting_widget_label2.grid(row=1, column=2,sticky='n')

setting_feeder_id = tk.StringVar()
setting_feeder_id.set(feeder_ids[0])  # 기본값을 설정합니다.
setting_feeder_id_menu = tk.OptionMenu(set_frame, setting_feeder_id, *feeder_ids)
setting_feeder_id_menu.grid(row=3, column=0,sticky='n')

mode_ids = ['auto', 'manual', 'stop']
selected_mode_id = tk.StringVar()
selected_mode_id.set(mode_ids[2])
mode_id_menu = tk.OptionMenu(set_frame, selected_mode_id, *mode_ids)
mode_id_menu.grid(row=3, column=1,sticky='n')
feed_size_ids = [3, 4, 5, 6]
selected_feed_size_ids = tk.StringVar()
selected_feed_size_ids.set(feed_size_ids[0])
feed_size_ids_menu = tk.OptionMenu(set_frame, selected_feed_size_ids, *feed_size_ids)
feed_size_ids_menu.grid(row=3, column=2,sticky='n')

setting_function_dict = {
    'set_feeding_mode': lambda: server.set_feeding_mode(selected_mode_id.get(),setting_feeder_id.get()),
    'set_feed_size': lambda: server.set_feed_size(selected_feed_size_ids.get(), setting_feeder_id.get()),
    'set_feeding_mode_all': server.set_feeding_mode_all,
    'set_feed_size_all': lambda: server.set_feed_size_all(selected_feed_size_ids.get())} 

for i, (button_text, button_function) in enumerate(setting_function_dict.items()):
    button = tk.Button(set_frame, text=button_text, command=button_function)
    if i > 1:
        button.grid(row=5, column=i-1,sticky='n')
    else:
        button.grid(row=4, column=i+1,sticky='n')

## Control 프레임에 내용 추가
control_feeder_id = tk.StringVar()
control_feeder_id.set(feeder_ids[0])  # 기본값을 설정합니다.
control_feeder_id_menu = tk.OptionMenu(control_frame, control_feeder_id, *feeder_ids)
control_feeder_id_menu.grid(row=2, column=1,sticky='n')

control_function_dict = {
    'stop_feeding': lambda: server.stop_feeding(control_feeder_id.get()),
    'manual_feeding': (lambda: server.manual_feeding(ast.literal_eval(manual_feeding_plan_entry.get())[0], ast.literal_eval(manual_feeding_plan_entry.get())[1], ast.literal_eval(manual_feeding_plan_entry.get())[2], control_feeder_id.get())),
    'stop_feeding_all': server.stop_feeding_all,
    'manual_feeding_all': lambda: server.manual_feeding_all(manual_feeding_plan_entry.get())}
    
# 각 함수에 대해 버튼을 생성합니다.
for i, (button_text, button_function) in enumerate(control_function_dict.items()):
    button = tk.Button(control_frame, text=button_text, command=button_function)
    if i > 1:
        button.grid(row=4, column=i-2,sticky='n')
    else:
        button.grid(row=5, column=i)

# UI를 실행합니다.
try:
    update_labels()
    root.mainloop()
except KeyboardInterrupt:
        print('사용자종료')
        root.destroy()