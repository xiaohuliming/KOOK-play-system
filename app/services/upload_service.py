import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def _get_ext(filename):
    """安全提取扩展名（不含点），避免 rsplit 越界。"""
    ext = os.path.splitext(str(filename or ''))[1].lower().lstrip('.')
    return ext


IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}
THUMB_MAX_SIZE = 128   # 缩略图最大边长 (px)
THUMB_QUALITY = 80     # 缩略图 WebP 质量
THUMB_PREFIX = 'thumb_'  # 缩略图文件名前缀


def allowed_file(filename):
    ext = _get_ext(filename)
    return bool(ext) and ext in current_app.config.get('ALLOWED_EXTENSIONS', set())


def _generate_thumbnail(source_path, thumb_path, max_size=THUMB_MAX_SIZE, quality=THUMB_QUALITY):
    """从原图生成缩略图 (WebP)。失败时静默跳过。"""
    try:
        from PIL import Image
        img = Image.open(source_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        img.save(thumb_path, format='WEBP', quality=quality, optimize=True)
        return True
    except Exception:
        return False


def get_thumb_path(image_path):
    """根据原图相对路径推算缩略图相对路径。
    e.g. 'uploads/gifts/abc.jpeg' → 'uploads/gifts/thumb_abc.webp'
    """
    if not image_path:
        return image_path
    directory = os.path.dirname(image_path)
    basename = os.path.basename(image_path)
    name_no_ext = os.path.splitext(basename)[0]
    thumb_name = f"{THUMB_PREFIX}{name_no_ext}.webp"
    return os.path.join(directory, thumb_name).replace('\\', '/')


def save_file(file, subfolder=''):
    """
    保存上传文件。图片类型会额外生成缩略图。
    :param file: 文件对象
    :param subfolder: 子目录 (e.g. 'avatars', 'gifts')
    :return: 原图相对路径, 错误信息
    """
    if file.filename == '':
        return None, '没有选择文件'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = _get_ext(file.filename) or _get_ext(filename)
        if not ext:
            return None, '文件扩展名无效'
        unique_name = uuid.uuid4().hex
        unique_filename = f"{unique_name}.{ext}"

        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 图片 → 额外生成缩略图 (原图保留不动)
        if ext in IMAGE_EXTENSIONS:
            thumb_name = f"{THUMB_PREFIX}{unique_name}.webp"
            thumb_path = os.path.join(upload_folder, thumb_name)
            _generate_thumbnail(file_path, thumb_path)

        relative_path = f"uploads/{subfolder}/{unique_filename}" if subfolder else f"uploads/{unique_filename}"
        return relative_path, None

    return None, '文件类型不支持'
