import cv2
from cv2 import VideoCapture
from cv2 import imwrite
import numpy as np
from PIL import Image
import os
import paddlehub
import paddlehub as hub

from encode_pic import BMPEncoder

# 去绿幕


def remove_green_background(img_path):
    img = cv2.imread(img_path)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # opencv 将BGR 转换成 HSV（绿色RGB：G-R>30&&G-B>30）
    # HSV指定绿色范围https://www.cnblogs.com/wangyblzu/p/5710715.html
    minGreen = np.array([35, 43, 46])
    maxGreen = np.array([77, 255, 255])
    # 确定绿色和非绿色范围
    mask = cv2.inRange(imgHSV, minGreen, maxGreen)
    mask_not = cv2.bitwise_not(mask)
    # 通过掩码控制的按位与运算锁定非绿色区域
    green_not = cv2.bitwise_and(img, img, mask=mask_not)
    b, g, r = cv2.split(green_not)  # 拆分为3通道
    bgra = cv2.merge([b, g, r, mask_not])  # 合成四通道
    # 保存带有透明通道的bmp图片,可以给这张图片替换任意背景
    # cv2.imwrite(out_path, bgra)
    return bgra


# 裁绿幕图片为正方形
def not_green_to_square(image):

    # 1. 扫描获得最左边透明点和最右边透明点坐标
    height, width, channel = image.shape  # 高、宽、通道数
    first_location = None  # 最先遇到的透明点
    last_location = None  # 最后遇到的透明点
    first_transparency = []  # 从左往右最先遇到的透明点，元素个数小于等于图像高度
    last_transparency = []  # 从左往右最后遇到的透明点，元素个数小于等于图像高度
    for y, rows in enumerate(image):
        for x, BGRA in enumerate(rows):
            alpha = BGRA[3]
            if alpha != 0:
                if not first_location or first_location[1] != y:  # 透明点未赋值或为同一列
                    first_location = (x, y)  # 更新最先遇到的透明点
                    first_transparency.append(first_location)
                last_location = (x, y)  # 更新最后遇到的透明点
        if last_location:
            last_transparency.append(last_location)

    # 2. 矩形四个边的中点
    top = first_transparency[0]
    bottom = first_transparency[-1]
    left = None
    right = None
    for first, last in zip(first_transparency, last_transparency):
        if not left:
            left = first
        if not right:
            right = last
        if first[0] < left[0]:
            left = first
        if last[0] > right[0]:
            right = last

    # 3. 左上角、右下角
    upper_left = (left[0], top[1])  # 左上角
    bottom_right = (right[0], bottom[1])  # 右下角

    box = upper_left[0], upper_left[1], bottom_right[0], bottom_right[1]
    result = image.copy()[box[1]:box[3], box[0]:box[2], :]

    result = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    result = result.convert('RGB')
    w, h = result.size
    region = Image.new('RGBA', size=(max(w, h), max(w, h)))  # 创建背景图，颜色值为127
    length = int(abs(w - h) // 2)  # 一侧需要填充的长度
    box = (length, 0) if w < h else (0, length)  # 粘贴的位置
    region.paste(result, box)
    return(region)
    # region.save(out_path)

# 调分辨率


def resize_img(region, file_out):
    width = 160
    height = 160
    resized_image = region.resize((width, height), Image.ANTIALIAS)
    resized_image.save(file_out)


def unnormal_green_background(in_path, out_path, i):
    # 读入
    in_address = os.path.join(in_path, 'IMG'+str(i)+'.jpg')
    # 处理
    bgra = remove_green_background(in_address)
    region = not_green_to_square(bgra)
    # 输出
    out_address = os.path.join(out_path, 'IMG'+str(i)+'.bmp')
    resize_img(region, out_address)
    out_address = os.path.join(out_path, 'IMG'+str(i)+'.jpg')
    region = region.convert('RGB')
    resize_img(region, out_address)


def recorded_notgreen_background(i):
    in_path = os.path.join('raw', 'recorded', str(i))  # 待读取的文件夹
    out_path = os.path.join('processed', 'recorded', str(i))  # 待写入的文件夹
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for j in range(1, 1+len(os.listdir(in_path))):
        unnormal_green_background(in_path, out_path, j)


def shot_notgreen_background(i):
    in_path = os.path.join('raw', 'shot')  # 待读取的文件夹
    out_path = os.path.join('processed', 'shot')  # 待写入的文件夹
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    unnormal_green_background(in_path, out_path, i)


# 裁非绿幕图片为正方形
def to_square(file_in):
    image = Image.open(file_in)
    img_size = image.size  # 图片的宽度和高度

    # 裁剪：元组元素：（距离图片左边界距离x， 距离图片上边界距离y，距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h）

    if(img_size[0] > img_size[1]):
        region = image.crop(
            ((img_size[0]-img_size[1])/2, 0, (img_size[0]-img_size[1])/2+img_size[1], img_size[1]))
    else:
        region = image.crop(
            (0, (img_size[1]-img_size[0])/2, img_size[0], (img_size[1]-img_size[0])/2+img_size[0]))
    # region.save(file_out)
    return region


# 非绿幕图片的处理
def normal(in_path, out_path, i):
    # 读入
    in_address = os.path.join(in_path, 'IMG'+str(i)+'.jpg')
    # 处理
    region = to_square(in_address)
    # 输出
    out_address = os.path.join(out_path, 'IMG'+str(i)+'.bmp')
    resize_img(region, out_address)
    out_address = os.path.join(out_path, 'IMG'+str(i)+'.jpg')
    region = region.convert('RGB')
    resize_img(region, out_address)


def recorded_normal(i):
    in_path = os.path.join('raw', 'recorded', str(i))  # 待读取的文件夹
    out_path = os.path.join('processed', 'recorded', str(i))  # 待写入的文件夹
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for j in range(1, 1+len(os.listdir(in_path))):
        normal(in_path, out_path, j)


def shot_normal(i):
    in_path = os.path.join('raw', 'shot')  # 待读取的文件夹
    out_path = os.path.join('processed', 'shot')  # 待写入的文件夹
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    normal(in_path, out_path, i)


def paddle_hub(in_path, out_path, i):
    # 读入
    in_address = os.path.join(in_path, 'IMG'+str(i)+'.jpg')
    # 分辨率太小了模型不识别人脸
    # region = Image.open(in_address)
    # resize_img(region, in_address)
    # 建立模型
    huseg = hub.Module(name='deeplabv3p_xception65_humanseg')
    # 裁剪图像
    results = huseg.segmentation(output_dir=out_path, data={
                                 'image': [in_address]}, visualization=True)  # 抠图
    in_address = os.path.join(out_path, 'IMG'+str(i)+'.png')
    region = Image.open(in_address)
    out_address = os.path.join(out_path, 'IMG'+str(i)+'.bmp')
    resize_img(region, out_address)


def recorded_paddlehub(i):
    in_path = os.path.join('raw', 'recorded', str(i))  # 待读取的文件夹
    out_path = os.path.join('processed', 'recorded', str(i))  # 待写入的文件夹
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for j in range(1, 1+len(os.listdir(in_path))):
        paddle_hub(in_path, out_path, i)


def shot_paddlehub(i):
    in_path = os.path.join('raw', 'shot')  # 待读取的文件夹
    out_path = os.path.join('processed', 'shot')  # 待写入的文件夹

    if not os.path.exists(out_path):
        os.mkdir(out_path)
    paddle_hub(in_path, out_path, i)


def shot_encode(i):
    in_path = os.path.join('raw', 'shot')  # 待读取的文件夹
    out_path = os.path.join('processed', 'shot')  # 待写入的文件夹

    bmp_path = os.path.join(in_path, 'IMG'+str(i)+'.bmp')
    hex_path = os.path.join(in_path, 'IMG'+str(i)+'.hex')

    encoder = BMPEncoder()
    encoder.transform(bmp_path, hex_path)


def recorded_encode(i):
    in_path = os.path.join('raw', 'recorded', str(i))  # 待读取的文件夹
    out_path = os.path.join('processed', 'recorded', str(i))  # 待写入的文件夹

    bmp_path = os.path.join(in_path, 'IMG'+str(i)+'.bmp')
    hex_path = os.path.join(in_path, 'IMG'+str(i)+'.hex')

    encoder = BMPEncoder()

    for pic in os.listdir(in_path):
        if 'bmp' in pic:
            bmp_path = os.path.join(in_path, pic)
            hex_path = os.path.join(out_path, pic.split('.')[0]+'.hex')
            encoder.transform(bmp_path, hex_path)


if __name__ == "__main__":
    # python3 process.py <type:img|vid> <id> <op:green|resize|face>
    import sys

    mode = sys.argv[1]
    id = int(sys.argv[2])
    op = sys.argv[3]

    try:
        if mode == "img":
            if op == "green":
                shot_notgreen_background(id)
            elif op == "resize":
                shot_normal(id)
            elif op == "face":
                shot_paddlehub(id)
            shot_encode(id)
        elif mode == "vid":
            if op == "green":
                recorded_notgreen_background(id)
            elif op == "resize":
                recorded_normal(id)
            elif op == "face":
                recorded_paddlehub(id)
            recorded_encode(id)
    except:
        exit(-1)
    exit(0)

    # recorded_notgreen_background(1)
    # shot_notgreen_background(2)
    # recorded_normal(1)
    # shot_normal(1)
    # recorded_paddlehub(1)
    # shot_paddlehub(16)
