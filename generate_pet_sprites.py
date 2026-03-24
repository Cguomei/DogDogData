"""
2.5D 宠物图片生成器
- 压缩现有图片
- 生成旋转视角效果
- 创建平滑过渡帧
"""
import os
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# 配置路径
INPUT_DIR = r'D:\PycharmProjects\fastApiProject\img\dog_pet'
OUTPUT_DIR = r'D:\PycharmProjects\fastApiProject\static\img\pet_sprites'
OPTIMIZED_DIR = r'D:\PycharmProjects\fastApiProject\static\img\pet_optimized'

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OPTIMIZED_DIR, exist_ok=True)


def compress_image(input_path, output_path, quality=85, max_size=(300, 300)):
    """
    压缩图片并优化
    """
    img = Image.open(input_path)
    
    # 转换为 RGBA（确保透明度）
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 缩放图片
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # 优化保存
    img.save(output_path, 'PNG', optimize=True, quality=quality)
    print(f"✅ 压缩完成：{output_path} ({img.size[0]}x{img.size[1]})")
    return img


def generate_rotation_frames(base_img, frames=8):
    """
    生成旋转视角的伪 3D 帧
    通过水平翻转和透视变换模拟 2.5D 效果
    """
    rotation_frames = []
    
    for i in range(frames):
        # 计算旋转角度（-45° 到 45°）
        angle = -45 + (90 / (frames - 1)) * i
        
        # 创建副本
        rotated = base_img.copy()
        
        # 应用轻微的水平缩放模拟透视
        if angle < 0:
            # 向左转
            scale_x = 1 + (abs(angle) / 90) * 0.2
            scale_y = 1 - (abs(angle) / 90) * 0.1
        elif angle > 0:
            # 向右转
            scale_x = 1 + (abs(angle) / 90) * 0.2
            scale_y = 1 - (abs(angle) / 90) * 0.1
        else:
            scale_x, scale_y = 1, 1
        
        # 应用缩放
        width, height = rotated.size
        new_size = (int(width * scale_x), int(height * scale_y))
        rotated = rotated.resize(new_size, Image.Resampling.LANCZOS)
        
        # 调整亮度和对比度模拟光照
        enhancer = ImageEnhance.Brightness(rotated)
        brightness = 1.0 + (abs(angle) / 90) * 0.15
        rotated = enhancer.enhance(brightness)
        
        enhancer = ImageEnhance.Contrast(rotated)
        contrast = 1.0 + (abs(angle) / 90) * 0.1
        rotated = enhancer.enhance(contrast)
        
        rotation_frames.append(rotated)
    
    return rotation_frames


def generate_smooth_transitions(frames_list, transition_frames=3):
    """
    在关键帧之间生成平滑过渡帧
    使用淡入淡出和位置渐变
    """
    smooth_frames = []
    
    for i in range(len(frames_list) - 1):
        current_frame = frames_list[i]
        next_frame = frames_list[i + 1]
        
        # 添加当前帧
        smooth_frames.append(current_frame)
        
        # 生成过渡帧
        for j in range(1, transition_frames + 1):
            alpha = j / (transition_frames + 1)
            
            # 创建过渡帧（交叉溶解）
            transition = Image.blend(current_frame, next_frame, alpha)
            smooth_frames.append(transition)
    
    # 添加最后一帧
    smooth_frames.append(frames_list[-1])
    
    return smooth_frames


def create_sprite_sheet(frames, output_path, columns=4):
    """
    将帧序列合并为精灵图（Sprite Sheet）
    """
    if not frames:
        return
    
    # 获取单帧尺寸
    frame_width, frame_height = frames[0].size
    
    # 计算精灵图尺寸
    rows = (len(frames) + columns - 1) // columns
    sheet_width = columns * frame_width
    sheet_height = rows * frame_height
    
    # 创建精灵图
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    # 粘贴每一帧
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        sprite_sheet.paste(frame, (col * frame_width, row * frame_height))
    
    # 保存
    sprite_sheet.save(output_path, 'PNG', optimize=True)
    print(f"✅ 精灵图已创建：{output_path} ({sheet_width}x{sheet_height}, {len(frames)}帧)")


def process_all_images():
    """
    处理所有原始图片
    """
    print("🎨 开始处理宠物图片...")
    
    # 获取所有输入图片
    image_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.png')]
    
    if not image_files:
        print(f"❌ 未找到图片文件：{INPUT_DIR}")
        return
    
    print(f"📂 找到 {len(image_files)} 张图片")
    
    # 分类处理
    eating_frames = []
    petting_frames = []
    idle_frames = []
    
    for img_file in image_files:
        input_path = os.path.join(INPUT_DIR, img_file)
        
        # 压缩图片
        optimized_path = os.path.join(OPTIMIZED_DIR, img_file)
        img = compress_image(input_path, optimized_path)
        
        # 根据文件名分类
        if '吃饭' in img_file:
            eating_frames.append(img)
        elif '摸摸' in img_file:
            petting_frames.append(img)
        else:
            idle_frames.append(img)
    
    # 生成旋转视角帧
    print("\n🔄 生成 2.5D 旋转视角...")
    if eating_frames:
        rotation_eating = generate_rotation_frames(eating_frames[0], frames=8)
        sprite_path = os.path.join(OUTPUT_DIR, 'eating_rotation.png')
        create_sprite_sheet(rotation_eating, sprite_path)
    
    # 生成平滑过渡帧
    print("\n✨ 生成平滑过渡动画...")
    if len(petting_frames) > 1:
        smooth_petting = generate_smooth_transitions(petting_frames, transition_frames=2)
        sprite_path = os.path.join(OUTPUT_DIR, 'petting_smooth.png')
        create_sprite_sheet(smooth_petting, sprite_path)
    
    # 为每个动作创建独立精灵图
    print("\n📋 创建动作精灵图...")
    
    # 吃饭动画
    if eating_frames:
        sprite_path = os.path.join(OUTPUT_DIR, 'eat_cycle.png')
        create_sprite_sheet(eating_frames, sprite_path)
    
    # 抚摸动画
    if petting_frames:
        sprite_path = os.path.join(OUTPUT_DIR, 'pet_cycle.png')
        create_sprite_sheet(petting_frames, sprite_path)
    
    # 待机动画（使用第一帧）
    if idle_frames:
        sprite_path = os.path.join(OUTPUT_DIR, 'idle.png')
        create_sprite_sheet(idle_frames[:1], sprite_path)
    
    print("\n✅ 所有图片处理完成！")
    print(f"📁 输出目录：{OUTPUT_DIR}")
    print(f"📁 优化目录：{OPTIMIZED_DIR}")


if __name__ == '__main__':
    try:
        process_all_images()
    except Exception as e:
        print(f"\n❌ 处理失败：{e}")
        import traceback
        traceback.print_exc()
