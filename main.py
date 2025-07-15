import customtkinter as ctk
from datetime import date, timedelta, datetime
from tkinter import PhotoImage
import csv
import sys
import os
import shutil

# 如果是打包后的程序，切换到可执行文件所在目录
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

def resource_path(relative_path):
    """获取资源文件的正确路径"""
    try:
        # PyInstaller打包后的临时文件夹
        base_path = sys._MEIPASS
        full_path = os.path.join(base_path, relative_path)
        return full_path
    except AttributeError:
        # 开发阶段直接使用当前目录
        full_path = os.path.join(os.path.abspath("."), relative_path)
        return full_path

# 设置主题 - 新的解决方案
theme_source = resource_path("mintcream_theme.json")
theme_target = "mintcream_theme.json"

print(f"主题源文件路径: {theme_source}")
print(f"主题目标路径: {theme_target}")

if os.path.exists(theme_source):
    # 将主题文件复制到当前工作目录
    shutil.copy2(theme_source, theme_target)
    print("主题文件复制成功")
    
    # 现在使用相对路径
    ctk.set_default_color_theme(theme_target)
    print("主题设置成功")
else:
    print(f"主题文件未找到: {theme_source}")
    # 使用内置主题作为备选
    ctk.set_default_color_theme("blue")
    print("使用内置蓝色主题")

# 处理图标文件
icon_path = resource_path("icon.png")
print(f"图标文件路径: {icon_path}")
print(f"图标文件是否存在: {os.path.exists(icon_path)}")

# ==== 初始化设置 ====
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("mintcream_theme.json")

window = ctk.CTk()
window.title("Task Tacker")
window.geometry("400x500")

# ==== 图标设置 ====
try:
    icon = PhotoImage(file="icon.png")
    window.iconphoto(True, icon)
except:
    pass

# ==== 创建滚动容器 ====
# 创建一个滚动框架来包含所有内容
scrollable_frame = ctk.CTkScrollableFrame(
    window, 
    width=380,  # Match the window width
    height=480,  # Match the window height
    fg_color="transparent",  # Make the frame transparent
    label_fg_color= "transparent",
    scrollbar_button_color="#d0d0d0",  # Light green color for scrollbar
    scrollbar_button_hover_color="#c0c0c0",  # Hover color for scrollbar
     # Smooth rounded corners for scrollbar
)
scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)  # Remove padding to make it fit the window

# ==== 变量初始化 ====
habits = []
checkbox_vars = {}
edit_mode = False

# ==== 加载任务列表 ====
def load_habits():
    global habits
    try:
        with open("habits_list.csv", "r") as f:
            reader = csv.reader(f)
            habits = [row[0] for row in reader if row]
    except FileNotFoundError:
        habits = ["Read for 30 minutes", "Exercise for 1 hour", "Sleep before 12pm"]

load_habits()

# ==== 顶部标题 ====
title_label = ctk.CTkLabel(scrollable_frame, text="Today's Tasks", font=("Segoe UI", 15, "bold"))
title_label.pack(pady=20)

# ==== 任务显示区域 ====
# 创建一个专门用于任务列表的容器，但不占用多余空间
habit_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent", corner_radius=0, border_width=0)
habit_frame.pack(pady=(10, 0), fill="x")

# ==== 渲染任务列表（含编辑模式支持） ====
def render_habit_list():
    for widget in habit_frame.winfo_children():
        widget.destroy()

    checkbox_vars.clear()

    for habit in habits:
        # 为每个任务创建单独的小框
        row = ctk.CTkFrame(habit_frame, corner_radius=10, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        row.pack(fill="x", pady=3, padx=25)

        var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(row, width=20, height=20, text=habit, variable=var)
        checkbox.pack(side="left", padx=12, pady=8)
        checkbox_vars[habit] = var

        if edit_mode:
            # 缩小删除按钮，使用统一的颜色样式
            del_button = ctk.CTkButton(row, text="✖", width=22, height=22, 
                                     fg_color="#ffcccc", text_color="#1d3557",
                                     hover_color="#76c8c8", font=("Segoe UI", 9, "bold"), 
                                     corner_radius=10, command=lambda h=habit: delete_task(h))
            del_button.pack(side="right", padx=8, pady=6)

# ==== 加载今日状态 ====
def load_today_status():
    today = date.today().isoformat()
    try:
        with open("habit_log.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 3:
                    continue
                date_str, habit_name, status_str = row
                if date_str == today and habit_name in checkbox_vars:
                    checkbox_vars[habit_name].set(status_str == "True")
    except FileNotFoundError:
        pass

# ==== 保存任务状态 ====
def save_progress():
    today = date.today().isoformat()
    today_records = [[today, habit, checkbox_vars[habit].get()] for habit in habits]

    try:
        with open("habit_log.csv", mode="r", newline="") as file:
            reader = list(csv.reader(file))
            updated_rows = [row for row in reader if row[0] != today]
    except FileNotFoundError:
        updated_rows = []

    updated_rows.extend(today_records)

    with open("habit_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

    completed = [habit for habit in habits if checkbox_vars[habit].get()]
    if completed:
        habit_list = "\n".join(f"✔ {habit}" for habit in completed)
        message = f"{today}\nYou completed {len(completed)} tasks:\n\n{habit_list}\nGood job!"
    else:
        message = f"{today} - No habits completed today. Keep going!"

    show_popup_frame("Save Progress", message)

# ==== 添加任务 ====
def add_task():
    pass  # 这个函数现在在show_popup_frame中处理

# ==== 保存任务列表 ====
def save_habits():
    with open("habits_list.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for habit in habits:
            writer.writerow([habit])

# ==== 删除任务 ====
def delete_task(task):
    if task in habits:
        habits.remove(task)
        save_habits()
        render_habit_list()

# ==== 切换编辑模式 ====
def toggle_edit_mode():
    global edit_mode
    edit_mode = not edit_mode
    delete_task_button.configure(text="Back" if edit_mode else "Delete Task")
    render_habit_list()

# ==== 显示添加任务框 ====
def show_add_task_frame():
    show_popup_frame("Add New Task", "", show_add_controls=True)

# ==== 隐藏弹出框 ====
def hide_popup_frame():
    popup_frame.pack_forget()

# ==== 通用弹出框显示函数 ====
def show_popup_frame(title, content, show_add_controls=False):
    # 清空之前的内容
    for widget in popup_frame.winfo_children():
        widget.destroy()
    
    # 创建一个容器，用于放置标题和关闭按钮
    header_frame = ctk.CTkFrame(popup_frame, fg_color="transparent", corner_radius=0, border_width=0)
    header_frame.pack(fill="x", pady=(5, 0), padx=(10, 10))  # Add padding to prevent blocking

    # close按钮
    close_button = ctk.CTkButton(header_frame, text="✖", command=hide_popup_frame, 
                                width=22, height=22, fg_color="#ffcccc", text_color="#1d3557",
                                hover_color="#76c8c8", font=("Segoe UI", 10, "bold"), corner_radius=11)
    close_button.pack(side="left", padx=(5, 5))

    # 标题
    title_label = ctk.CTkLabel(header_frame, text=title, text_color="#1d3557", font=("Segoe UI", 12, "bold"))
    title_label.pack(side="left", padx=(5, 10))

    # 内容
    if content:
        content_label = ctk.CTkLabel(popup_frame, text=content, text_color="#1d3557", font=("Segoe UI", 12))
        content_label.pack(pady=(10, 10))
    
    # 添加任务控件
    if show_add_controls:
        add_task_entry = ctk.CTkEntry(popup_frame, placeholder_text="Enter New Task", width=300)
        add_task_entry.pack(pady=10)
        
        def add_task_from_popup():
            task = add_task_entry.get().strip()
            if task and task not in habits:
                habits.append(task)
                save_habits()
                render_habit_list()
                add_task_entry.delete(0, "end")
        
        confirm_add_button = ctk.CTkButton(popup_frame, text="Confirm Add", command=add_task_from_popup)
        confirm_add_button.pack(pady=(0, 10))
    
    # 显示弹出框并自动滚动到底部以确保弹出框可见
    popup_frame.pack(pady=30, padx=25, fill="x")
    
    # 自动滚动到弹出框位置
    scrollable_frame.after(10, lambda: scrollable_frame._parent_canvas.yview_moveto(1.0))

# ==== 周总结 ====
def view_summary():
    popup_frame.pack(pady=10, padx=25, fill="x")
    # 清空之前的内容
    for widget in popup_frame.winfo_children():
        widget.destroy()
    
    temp_label = ctk.CTkLabel(popup_frame, text="Loading...", text_color="#1d3557", font=("Segoe UI", 12))
    temp_label.pack(pady=10)
    
    scrollable_frame.after(100, really_view_summary)

def really_view_summary():
    # 清空loading文字
    for widget in popup_frame.winfo_children():
        widget.destroy()
    
    summary = {habit: 0 for habit in habits}
    today = date.today()
    week_ago = today - timedelta(days=6)

    try:
        with open("habit_log.csv", mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != 3:
                    continue
                date_str, habit_name, status_str = row
                row_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if week_ago <= row_date <= today and habit_name in summary:
                    if status_str == "True":
                        summary[habit_name] += 1
    except:
        show_popup_frame("Weekly Summary", "No progress saved yet.")
        return

    # 构建总结内容
    summary_text = f"({week_ago}~{today}):\n\n"
    for habit, count in summary.items():
        summary_text += f"✔ {habit}: {count} days\n"
    
    show_popup_frame("Weekly Summary", summary_text)

# ==== 隐藏总结框 ====
def hide_summary():
    popup_frame.pack_forget()

# ==== 控件区域 ====
save_button = ctk.CTkButton(scrollable_frame, text="Save Today's Progress", command=save_progress)
save_button.pack(pady=10)

add_button = ctk.CTkButton(scrollable_frame, text="Add a New Task", command=show_add_task_frame)
add_button.pack(pady=5)

delete_task_button = ctk.CTkButton(scrollable_frame, text="Delete Task", command=toggle_edit_mode)
delete_task_button.pack(pady=5)

summary_button = ctk.CTkButton(scrollable_frame, text="View Weekly Summary", command=view_summary)
summary_button.pack(pady=10)

# ==== 通用弹出框 ====
popup_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="white")
popup_frame.pack_forget()

# ==== 启动程序 ====
render_habit_list()
load_today_status()
window.mainloop()