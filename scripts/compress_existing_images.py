#!/usr/bin/env python3
"""
一次性脚本: 为 static/uploads/ 下的已有图片生成缩略图。
原图保持不动，额外生成 thumb_xxx.webp 缩略图文件。

用法: python scripts/compress_existing_images.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app', 'static', 'uploads')
THUMB_MAX_SIZE = 128
THUMB_QUALITY = 80
THUMB_PREFIX = 'thumb_'
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}


def generate_thumbnail(src_path):
    """为单张图片生成缩略图，返回缩略图路径或 None"""
    ext = os.path.splitext(src_path)[1].lower()
    if ext not in IMAGE_EXTS:
        return None

    basename = os.path.basename(src_path)
    # 跳过已有的缩略图
    if basename.startswith(THUMB_PREFIX):
        return None

    directory = os.path.dirname(src_path)
    name_no_ext = os.path.splitext(basename)[0]
    thumb_path = os.path.join(directory, f"{THUMB_PREFIX}{name_no_ext}.webp")

    # 已有缩略图则跳过
    if os.path.exists(thumb_path):
        print(f"  跳过 (缩略图已存在): {basename}")
        return None

    try:
        img = Image.open(src_path)
        original_size = os.path.getsize(src_path)

        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        img.thumbnail((THUMB_MAX_SIZE, THUMB_MAX_SIZE), Image.LANCZOS)
        img.save(thumb_path, format='WEBP', quality=THUMB_QUALITY, optimize=True)
        thumb_size = os.path.getsize(thumb_path)

        print(f"  ✅ {basename} → {os.path.basename(thumb_path)}  "
              f"({original_size // 1024}KB → {thumb_size // 1024}KB)")
        return thumb_path
    except Exception as e:
        print(f"  ❌ 失败 {basename}: {e}")
        return None


def main():
    if not os.path.exists(UPLOAD_ROOT):
        print(f"上传目录不存在: {UPLOAD_ROOT}")
        return

    all_images = []
    for root, dirs, files in os.walk(UPLOAD_ROOT):
        for f in files:
            fp = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if ext in IMAGE_EXTS and not f.startswith(THUMB_PREFIX) and not f.endswith('.bak'):
                all_images.append(fp)

    print(f"找到 {len(all_images)} 张原图，开始生成缩略图...\n")

    count = 0
    for fp in all_images:
        result = generate_thumbnail(fp)
        if result:
            count += 1

    print(f"\n✅ 完成! 共生成 {count} 张缩略图，原图保持不变。")


if __name__ == '__main__':
    main()
