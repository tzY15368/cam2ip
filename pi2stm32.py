import serial
import os

com0 = '/dev/rfcomm0'  # 蓝牙端口
bd = 38400  # 波特率
# 蓝牙连接


def send_video(fpath, ftype='bmp'):
    # 参数1：视频存储路径；参数2：目标图片格式(默认bmp)
    os.system('sudo rfcomm bind 0 98:D3:31:F7:49:A4')  # 连接蓝牙
    picnums = 0  # 图片总数
    picnow = 0  # 图片序号
    for pic in os.listdir(fpath):
        if ftype in pic:
            picnums += 1
    picnumsbin = picnums.to_bytes(length=2, byteorder='big', signed=False)
    # 传输每张图片
    for pic in os.listdir(fpath):
        if ftype in pic:
            try:
                ser = serial.Serial(com0, bd)
                picnowbin = picnow.to_bytes(
                    length=2, byteorder='big', signed=False)
                picnow += 1
                with open(fpath+'/'+pic, 'rb') as f:
                    a = f.read()
                # 添加图片总数和编号
                # a = picnumsbin+picnowbin+a
                ser.write(a)
            except Exception as e:
                print("VideoException:", e)


# 发送单张图片
def send_photo(ppath):  # 参数：图片完整路径
    os.system('sudo rfcomm bind 0 98:D3:31:F7:49:A4')  # 连接蓝牙
    try:
        ser = serial.Serial(com0, bd)
        with open(ppath, 'rb') as f:
            a = f.read()
        # 添加图片总数和编号
        # a = b'\x00\x01'+b'\x00\x00'+a
        ser.write(a)
    except Exception as e:
        print("PhotoException:", e)

if __name__ == "__main__":
    import sys,os
    otype = sys.argv[1]
    id = sys.argv[2]
    # python3 pi2stm32.py <type:vid|img> <id:int>
    try:
        if otype == "vid":
            send_video(os.path.join("raw","recorded",str(id)))
        elif otype == "img":
            send_photo(os.path.join("raw","shot",str(id)))
        exit(0)    
    except:
        exit(-1)
