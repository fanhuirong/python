# coding:utf-8
# 将照片的文件名改为拍摄时间
# python3 /Users/kunkunfan/Downloads/code/\ python/format_photoname.py
# eg: 打开 终端 (Terminal)，然后将文件或文件夹直接拖入终端窗口，它会自动显示完整路径。

import os
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import shutil

def get_exif_data(image_path):
    """
    获取图片的EXIF数据
    """
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

def get_date_taken(image_path):
    """
    获取照片拍摄时间，如果无法获取则返回文件修改时间
    """
    exif_data = get_exif_data(image_path)
    
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

def rename_photos(folder_path):
    """
    重命名文件夹中的所有照片
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在或不是一个目录")
        return
    
    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic']
    
    # 遍历文件夹中的所有文件
    renamed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # 检查是否为文件且扩展名为图片格式
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
            try:
                # 获取照片拍摄时间
                date_taken = get_date_taken(file_path)
                
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
        else:
            # 只有当文件是普通文件但不是支持的图片格式时才计入跳过数
            if os.path.isfile(file_path):
                skipped_count += 1
                print(f"跳过非图片文件: {filename}")
    
    print(f"\n重命名完成! 已重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文件。")
if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        rename_photos(folder_path)
    else:
        folder_path = input("请输入照片文件夹路径: ")
        rename_photos(folder_path)