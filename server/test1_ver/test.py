import tkinter as tk

# Tk 객체를 생성합니다.
root = tk.Tk()

frame = tk.Frame(root)
frame.pack(fill='both', expand=True)
# Canvas 객체를 생성합니다.
canvas = tk.Canvas(frame)
canvas.pack(side='left', fill='both', expand=True)

# Scrollbar 객체를 생성합니다.
scrollbar = tk.Scrollbar(frame, command=canvas.yview)
scrollbar.pack(side='left', fill='y')

# Canvas에 Scrollbar를 연결합니다.
canvas.configure(yscrollcommand=scrollbar.set)

# Frame 객체를 생성하고 Canvas에 추가합니다.
frame = tk.Frame(canvas)
canvas.create_window((0,0), window=frame, anchor='nw')

# Frame에 위젯을 추가합니다.
for i in range(100):
    tk.Label(frame, text='Label %s' % i).pack()

# Frame의 크기가 변경될 때 Canvas의 스크롤 영역을 업데이트합니다.
frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

root.mainloop()