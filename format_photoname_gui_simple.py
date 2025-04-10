# coding:utf-8
# 将照片的文件名改为拍摄时间（简化版可视化界面）
# python3 /Users/kunkunfan/Downloads/code/\ python/format_photoname_gui_simple.py

import os
import sys
import threading
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkFont

# RedirectText类保持不变
class RedirectText:
    """用于重定向控制台输出到GUI文本框"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass

class PhotoRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("照片重命名工具")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")
        
        # 设置字体
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.normal_font = tkFont.Font(family="Helvetica", size=12)
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        self.title_label = tk.Label(
            self.main_frame, 
            text="照片重命名工具", 
            font=self.title_font,
            bg="#f0f0f0"
        )
        self.title_label.pack(pady=(0, 20))
        
        # 说明文本
        self.instruction_label = tk.Label(
            self.main_frame,
            text="点击下方按钮选择照片文件夹",
            font=self.normal_font,
            bg="#f0f0f0"
        )
        self.instruction_label.pack(pady=(0, 10))
        
        # 文件夹显示区域
        self.folder_frame = tk.LabelFrame(
            self.main_frame,
            text="选择的文件夹",
            bg="#ffffff",
            font=self.normal_font,
            width=600,
            height=100
        )
        self.folder_frame.pack(fill=tk.X, pady=10)
        
        self.folder_label = tk.Label(
            self.folder_frame,
            text="尚未选择文件夹",
            bg="#ffffff",
            font=self.normal_font
        )
        self.folder_label.pack(expand=True, fill=tk.BOTH)
        
        # 按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.browse_button = tk.Button(
            self.button_frame,
            text="选择文件夹",
            command=self.browse_folder,
            font=self.normal_font,
            bg="#4CAF50",
            fg="black",
            padx=10
        )
        self.browse_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_button = tk.Button(
            self.button_frame,
            text="开始重命名",
            command=self.start_renaming,
            font=self.normal_font,
            bg="#2196F3",
            fg="black",
            padx=10,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 日志区域
        self.log_frame = tk.LabelFrame(
            self.main_frame,
            text="处理日志",
            bg="#ffffff",
            font=self.normal_font
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = ScrolledText(
            self.log_frame,
            state="disabled",
            bg="#ffffff",
            font=("Courier", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 重定向标准输出到日志文本框
        self.text_redirect = RedirectText(self.log_text)
        sys.stdout = self.text_redirect
        
        # 初始化变量
        self.folder_path = None
        self.is_processing = False
    
    def browse_folder(self, event=None):
        """打开文件夹选择对话框"""
        folder_path = filedialog.askdirectory(title="选择照片文件夹")
        if folder_path:
            self.folder_path = folder_path
            self.folder_label.config(text=f"已选择: {folder_path}")
            self.start_button.config(state=tk.NORMAL)
    
    # 其余方法保持不变
    def start_renaming(self):
        """开始重命名过程"""
        if not self.folder_path or not os.path.isdir(self.folder_path):
            messagebox.showerror("错误", "请先选择有效的文件夹")
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        
        # 清空日志
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
        
        # 在新线程中运行重命名操作
        threading.Thread(target=self.rename_photos_thread, daemon=True).start()
    
    def rename_photos_thread(self):
        """在单独的线程中运行重命名操作"""
        try:
            print(f"开始处理文件夹: {self.folder_path}\n")
            self.rename_photos(self.folder_path)
            self.root.after(0, self.on_renaming_complete)
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            self.root.after(0, self.on_renaming_error, str(e))
    
    def on_renaming_complete(self):
        """重命名完成后的回调"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        messagebox.showinfo("完成", "照片重命名已完成")
    
    def on_renaming_error(self, error_msg):
        """重命名出错后的回调"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        messagebox.showerror("错误", f"处理过程中发生错误:\n{error_msg}")
    
# ... 现有代码保持不变 ...

    def on_renaming_error(self, error_msg):
        """重命名出错后的回调"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        messagebox.showerror("错误", f"处理过程中发生错误:\n{error_msg}")
    
    def get_exif_data(self, image_path):
        """获取图片的EXIF数据"""
        try:
            image = Image.open(image_path)
            exif_data = {}
            info = image._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    exif_data[decoded] = value
                return exif_data
            return None
        except Exception as e:
            print(f"无法读取EXIF数据: {e}")
            return None

    def get_date_taken(self, image_path):
        """获取照片拍摄时间，如果无法获取则返回文件修改时间"""
        exif_data = self.get_exif_data(image_path)
        
        # 尝试从EXIF数据中获取拍摄时间
        if exif_data and "DateTimeOriginal" in exif_data:
            date_str = exif_data["DateTimeOriginal"]
            try:
                # EXIF日期格式通常为 "YYYY:MM:DD HH:MM:SS"
                date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                return date_obj
            except ValueError:
                print(f"无法解析EXIF日期: {date_str}")
        
        # 如果无法从EXIF获取，则使用文件修改时间
        mod_time = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mod_time)

    def rename_photos(self, folder_path):
        """重命名文件夹中的所有照片"""
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"错误: 文件夹 '{folder_path}' 不存在或不是一个目录")
            return
        
        # 支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic']
        
        # 获取所有文件
        all_files = [f for f in os.listdir(folder_path) 
                    if os.path.isfile(os.path.join(folder_path, f))]
        
        # 筛选图片文件
        image_files = [f for f in all_files 
                      if os.path.splitext(f)[1].lower() in image_extensions]
        
        total_images = len(image_files)
        if total_images == 0:
            print("文件夹中没有找到支持的图片文件")
            return
        
        print(f"找到 {total_images} 个图片文件，开始处理...\n")
        
        # 遍历文件夹中的所有文件
        renamed_count = 0
        skipped_count = 0
        
        for i, filename in enumerate(image_files):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # 更新进度条
                progress = (i + 1) / total_images * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # 获取照片拍摄时间
                date_taken = self.get_date_taken(file_path)
                
                # 格式化新文件名
                new_filename = date_taken.strftime("%Y-%m-%d_%Hh%Mm%Ss") + os.path.splitext(filename)[1]
                new_file_path = os.path.join(folder_path, new_filename)
                
                # 如果新文件名已存在，添加序号
                counter = 1
                while os.path.exists(new_file_path):
                    new_filename = date_taken.strftime("%Y-%m-%d_%Hh%Mm%Ss") + f"_{counter}" + os.path.splitext(filename)[1]
                    new_file_path = os.path.join(folder_path, new_filename)
                    counter += 1
                
                # 重命名文件
                shutil.copy2(file_path, new_file_path)  # 使用copy2保留文件元数据
                os.remove(file_path)  # 删除原文件
                print(f"已重命名: {filename} -> {new_filename}")
                renamed_count += 1
                
            except Exception as e:
                print(f"处理文件 '{filename}' 时出错: {e}")
                skipped_count += 1
        
        print(f"\n重命名完成! 已重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文件。")

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoRenamerApp(root)
    root.mainloop()
