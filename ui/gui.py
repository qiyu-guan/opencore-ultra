# ui/gui.py - Tkinter图形界面
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from core import device, backup, flash, firmware, root, system, rescue
from config import GUI_TITLE, GUI_GEOMETRY

class OpenCoreGUI:
    def __init__(self, master):
        self.master = master
        master.title(GUI_TITLE)
        master.geometry(GUI_GEOMETRY)
        self.create_menu()
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.create_tabs()
        self.status = tk.Label(master, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="切换至命令行", command=self.switch_to_cli)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.master.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.master.config(menu=menubar)

    def switch_to_cli(self):
        self.master.destroy()
        from ui.cli import run_cli
        run_cli()

    def create_tabs(self):
        tabs = [
            ("设备", self.create_device_tab),
            ("备份", self.create_backup_tab),
            ("刷机", self.create_flash_tab),
            ("固件", self.create_firmware_tab),
            ("Root", self.create_root_tab),
            ("系统", self.create_system_tab),
            ("救砖", self.create_rescue_tab),
        ]
        for name, func in tabs:
            frame = ttk.Frame(self.notebook)
            func(frame)
            self.notebook.add(frame, text=name)

    def create_device_tab(self, frame):
        tk.Label(frame, text="设备信息").pack()
        self.dev_info = tk.Text(frame, height=10, width=80)
        self.dev_info.pack(padx=10, pady=5)
        tk.Button(frame, text="刷新", command=self.refresh_device).pack()

    def refresh_device(self):
        mode, dev, info = device.detect_device()
        self.dev_info.delete(1.0, tk.END)
        self.dev_info.insert(tk.END, f"模式: {mode}\n设备: {dev}\n信息: {info}")

    def create_backup_tab(self, frame):
        tk.Button(frame, text="字库备份", command=self.do_full_backup).pack(pady=5)
        tk.Button(frame, text="分区备份", command=self.do_part_backup).pack(pady=5)
        tk.Button(frame, text="应用备份", command=self.do_app_backup).pack(pady=5)

    def do_full_backup(self):
        threading.Thread(target=self._run_full_backup).start()

    def _run_full_backup(self):
        mode, dev, _ = device.detect_device()
        if mode != 'adb':
            messagebox.showerror("错误", "仅ADB模式支持字库备份")
            return
        out_dir = filedialog.askdirectory(title="选择备份目录")
        if out_dir:
            if backup.full_flash_backup(dev, Path(out_dir)):
                messagebox.showinfo("成功", "字库备份完成")
            else:
                messagebox.showerror("失败", "字库备份失败")

    def do_part_backup(self):
        # 类似实现
        pass

    def do_app_backup(self):
        pass

    def create_flash_tab(self, frame):
        tk.Button(frame, text="刷入分区", command=self.do_fastboot_flash).pack(pady=5)
        tk.Button(frame, text="刷入Recovery", command=self.do_flash_recovery).pack(pady=5)
        tk.Button(frame, text="刷入线刷包", command=self.do_flash_zip).pack(pady=5)

    def do_fastboot_flash(self):
        mode, dev, _ = device.detect_device()
        if mode != 'fastboot':
            messagebox.showerror("错误", "请进入fastboot模式")
            return
        part = tk.simpledialog.askstring("输入", "分区名")
        img = filedialog.askopenfilename(title="选择镜像")
        if part and img:
            if flash.fastboot_flash(dev, part, img):
                messagebox.showinfo("成功", "刷入成功")
            else:
                messagebox.showerror("失败", "刷入失败")

    def do_flash_recovery(self):
        mode, dev, _ = device.detect_device()
        if mode != 'fastboot':
            messagebox.showerror("错误", "请进入fastboot模式")
            return
        img = filedialog.askopenfilename(title="选择Recovery镜像")
        if img:
            if flash.flash_custom_recovery(dev, img):
                messagebox.showinfo("成功", "Recovery刷入成功")
            else:
                messagebox.showerror("失败", "Recovery刷入失败")

    def do_flash_zip(self):
        zip_path = filedialog.askopenfilename(title="选择线刷包")
        if zip_path:
            mode, dev, _ = device.detect_device()
            if mode != 'fastboot':
                messagebox.showerror("错误", "请进入fastboot模式")
                return
            if flash.fastboot_flash_all(zip_path, dev):
                messagebox.showinfo("成功", "线刷包刷入完成")
            else:
                messagebox.showerror("失败", "刷入失败")

    def create_firmware_tab(self, frame):
        tk.Label(frame, text="固件管理功能").pack()

    def create_root_tab(self, frame):
        tk.Label(frame, text="Root与模块管理").pack()

    def create_system_tab(self, frame):
        tk.Label(frame, text="系统修改与优化").pack()

    def create_rescue_tab(self, frame):
        tk.Button(frame, text="进入EDL模式", command=self.do_edl_enter).pack(pady=5)
        tk.Button(frame, text="EDL信息", command=self.do_edl_info).pack(pady=5)
        tk.Button(frame, text="擦除FRP", command=self.do_frp_reset).pack(pady=5)

    def do_edl_enter(self):
        mode, dev, _ = device.detect_device()
        if mode != 'adb':
            messagebox.showerror("错误", "请先连接ADB")
            return
        if rescue.edl_enter(dev):
            messagebox.showinfo("成功", "已尝试进入EDL模式")
        else:
            messagebox.showerror("失败", "进入EDL失败")

    def do_edl_info(self):
        info = rescue.edl_info()
        messagebox.showinfo("EDL信息", info)

    def do_frp_reset(self):
        if messagebox.askyesno("警告", "此操作将清除FRP锁，确认设备所有权?"):
            mode, dev, _ = device.detect_device()
            if mode == 'adb':
                if rescue.frp_reset(dev):
                    messagebox.showinfo("成功", "FRP重置成功")
                else:
                    messagebox.showerror("失败", "FRP重置失败")

def run_gui():
    root = tk.Tk()
    app = OpenCoreGUI(root)
    root.mainloop()
