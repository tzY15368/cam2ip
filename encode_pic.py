from struct import unpack, pack
import math


class BMPEncoder:

    encode_table = []

    def __init__(self):
        self.init_encode_table()

    def transform(self, input_file_name, output_file_name):
        self.read_file(input_file_name)
        self.white_balance()
        self.encode_pic()
        self.save_file(output_file_name)

    def read_file(self, file_name):
        file = open(file_name, "rb")
        # 读取 bmp 文件的文件头    14 字节
        # 0x4d42 对应BM 表示这是Windows支持的位图格式
        self.bfType = unpack("<h", file.read(2))[0]
        self.bfSize = unpack("<i", file.read(4))[0]       # 位图文件大小
        self.bfReserved1 = unpack("<h", file.read(2))[0]  # 保留字段 必须设为 0
        self.bfReserved2 = unpack("<h", file.read(2))[0]  # 保留字段 必须设为 0
        # 偏移量 从文件头到位图数据需偏移多少字节（位图信息头、调色板长度等不是固定的，这时就需要这个参数了）
        self.bfOffBits = unpack("<i", file.read(4))[0]
        # 读取 bmp 文件的位图信息头 40 字节
        self.biSize = unpack("<i", file.read(4))[0]       # 所需要的字节数
        self.biWidth = unpack("<i", file.read(4))[0]      # 图像的宽度 单位 像素
        self.biHeight = unpack("<i", file.read(4))[0]     # 图像的高度 单位 像素
        self.biPlanes = unpack("<h", file.read(2))[0]     # 说明颜色平面数 总设为 1
        self.biBitCount = unpack("<h", file.read(2))[0]   # 说明比特数

        self.biCompression = unpack("<i", file.read(4))[0]  # 图像压缩的数据类型
        self.biSizeImage = unpack("<i", file.read(4))[0]    # 图像大小
        self.biXPelsPerMeter = unpack("<i", file.read(4))[0]  # 水平分辨率
        self.biYPelsPerMeter = unpack("<i", file.read(4))[0]  # 垂直分辨率
        self.biClrUsed = unpack("<i", file.read(4))[0]      # 实际使用的彩色表中的颜色索引数
        self.biClrImportant = unpack("<i", file.read(4))[
            0]  # 对图像显示有重要影响的颜色索引的数目
        self.bmp_data = []

        if self.biBitCount != 24:
            print("输入的图片比特值为 ：" + str(self.biBitCount) + "\t 与程序不匹配")

        for height in range(self.biHeight):
            bmp_data_row = []
            # 四字节填充位检测
            count = 0
            for width in range(self.biWidth):
                bmp_data_row.append([unpack("<B", file.read(1))[0], unpack(
                    "<B", file.read(1))[0], unpack("<B", file.read(1))[0]])
                count = count + 3
            # bmp 四字节对齐原则
            while count % 4 != 0:
                file.read(1)
                count = count + 1
            self.bmp_data.append(bmp_data_row)
        self.bmp_data.reverse()
        file.close()

        # self.bmp_data[row][col][0 1 2] B G R

    def save_file(self, file_name):
        bts = b''
        for line in self.encoded_data:
            for p in line:
                bts += pack('BBB', p[0], p[1], p[2])
        with open(file_name, 'wb') as f:
            f.write(bts)

    def init_encode_table(self):

        degree_range = []
        for i in range(240):
            degree_range.append(i*1.5)

        r_range = []
        for j in range(160):
            r_range.append(79.5 - j)

        self.encode_table = []
        for degree in degree_range:
            table_line = []
            for r in r_range:
                seita = math.radians(degree)
                # y up, x right
                x = int(round(r * math.cos(seita)+79.5))
                y = int(round(r * math.sin(seita)+79.5))
                table_line.append([x, y])
            self.encode_table.append(table_line)

    def white_balance(self):
        for line in self.bmp_data:
            for p in line:
                p[0] = int(p[0] * 0.7)  # G
                p[1] = int(p[1] * 0.7)  # B
                p[2] = int(p[2])  # R

    def encode_pic(self):
        self.encoded_data = []
        for table_line in self.encode_table:
            data_line = []
            for index in range(0, len(table_line)):
                y = table_line[index][0]
                x = 159 - table_line[index][1]
                data_line.append(
                    [
                        255-round(i*abs(79.5 - index)/79.5)
                        for i in reversed(self.bmp_data[x][y])
                    ]
                )
            self.encoded_data.append(data_line)


if __name__ == '__main__':
    bmp_pic = BMPEncoder()
    bmp_pic.transform('./black.bmp', './encode.hex')
    print("done")
