'''
人脸关键点手动标注
'''

import os
import re
import numpy as np
from numpy import *
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
import PFLD
import logging
import logging.handlers

logging.FileHandler(filename='Face_data_mark.log', mode='a', encoding='utf-8')
logging.basicConfig(filename='Face_data_mark.log', filemode='a', level=logging.INFO)

class Point_Move:
    showverts = True
    offset = 3  # 距离偏差设置

    def __init__(self, img_path):

        # 消重
        filename = os.path.basename(img_path)
        f = open('Face_data_mark.log', 'rb')
        a = f.readlines()
        matchObj = re.search(filename, "%s" % a, re.M | re.I)
        if matchObj:
            print(img_path + " 已标记过")
        else:
            print("正在标记：" + str(img_path))
            # 设置显示图片
            im = Image.open(img_path)
            # im = im.transpose(Image.FLIP_TOP_BOTTOM)

            # 创建figure（绘制面板）、创建图表（axes）
            self.fig, self.ax = plt.subplots()
            plt.imshow(im)
            # 设置标题
            self.ax.set_title(img_path + "\n" +
                              'Click and drag a point to move it, this will update the ax txt!')
            # 设置坐标轴范围
            self.img_size = im.size
            self.ax.set_xlim(0, self.img_size[0])  # 图片像素宽度
            self.ax.set_ylim(0, self.img_size[1])  # 图片像素高度
            self.ax.xaxis.set_ticks_position('top')  # 将x轴的位置设置在顶部
            self.ax.invert_yaxis()  # y轴反向
            # 设置关键点初始值
            self.x, self.y = self.getFacePoit(img_path) # 调用模型或读取标签文件中关键点坐标信息
            # 绘制2D的动画line
            self.line = Line2D(self.x, self.y, ls="", marker='.',
                                markersize=2, markerfacecolor='g', animated=True)
            self.ax.add_line(self.line)
            # 标志值设为none
            self._ind = None
            # 设置画布，方便后续画布响应事件
            canvas = self.fig.canvas
            self.fig.canvas.mpl_connect('draw_event', self.draw_callback)
            self.fig.canvas.mpl_connect('button_press_event', self.button_press_callback)
            self.fig.canvas.mpl_connect('button_release_event', self.button_release_callback)
            self.fig.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
            self.canvas = canvas
            # plt.grid()
            plt.show()


    # 界面重新绘制
    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        # 在公差允许的范围内，求出鼠标点下顶点坐标的数值
        xt, yt = np.array(self.x), np.array(self.y)
        # print(str(xt) + " " + str(self.img_size[1] - yt))
        d = np.sqrt((xt-event.xdata)**2 + (yt-event.ydata)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        # print(str(indseq))
        ind = indseq[0]
        print(str(indseq[0]))
        # 如果在公差范围内，则返回ind的值
        if d[ind] >=self.offset:
            ind = None
        return ind

    # 鼠标被按下，立即计算最近的顶点下标
    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts: return
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event)

    # 鼠标释放后，清空、重置
    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts: return
        if event.button != 1: return
        # 更新当前点坐标信息
        lineNum = self._ind + 4
        print("Replace line num = " + str(lineNum))
        newLine = '%.7s' % str(event.xdata) + " " + '%.7s' % str(event.ydata) + "\n"
        print("New line = " + newLine)
        self.replaceLine(self.txt_path, lineNum, newLine)
        # 重置标签序号
        self._ind = None

    # 鼠标移动的事件
    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        # 更新数据
        x, y = event.xdata, event.ydata
        self.x[self._ind] = x
        self.y[self._ind] = y
        # 根据更新的数值，重新绘制图形
        self.line = Line2D(self.x, self.y, ls="", marker='.',
                           markersize=2, markerfacecolor='g', animated=True)
        self.ax.add_line(self.line)
        # 恢复背景
        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)



    def getFacePoit(self, img_path):
        """
        根据标签文件中的坐标在人脸图片上绘制关键点
        :param img_path: 待标注图片路径
        :param txt_path: 标注文件路径
        :return:
        """

        x = []
        y = []
        self.txt_path = ""
        # 根据图片路径求得标签文件路径
        if os.path.splitext(img_path)[1] == '.jpg' or os.path.splitext(img_path)[1] == '.png':
            fileName = os.path.splitext(img_path)[0]
            self.txt_path = fileName + ".pts"
            # 判断标签文件后是否存在
            if not os.path.exists(self.txt_path):
                with open(self.txt_path, 'a') as fw:
                    fw.write("version: 1" + "\n")
                    fw.write("n_points: 68" + "\n")
                    fw.write("{" + "\n")
                    # fw.write("0 0 0 0 0 0" + "\n")
                    fw.close()
                # 调用模型输出并写入预测关键点坐标
                try:
                    landmarks, x1, y1 = PFLD.getLandMarks(img_path)
                    # if landmarks is not None:
                    for (x0, y0) in landmarks.astype(np.float32):
                        with open(self.txt_path, 'a') as fw:
                            fw.write('%.7s' % str(x0+x1) + " " + '%.7s' % str(y0+y1) + "\n")
                            fw.close()
                        x.append(float('%.7s' % str(x0+x1)))
                        y.append(float('%.7s' % str((y0+y1))))
                    with open(self.txt_path, 'a') as fw:
                        fw.write("}")
                        fw.close()
                except Exception:
                    os.remove(self.txt_path)
                    print("该图片未检测到人脸，无法输出标签数据")
            else:
                # 直接读取标签文件获取关键点信息
                try:
                    num_of_line = 1
                    with open(self.txt_path, 'r') as f:
                        while True:
                            line = f.readline()
                            print(line)
                            if num_of_line <= 4:
                                print("非坐标行")
                            elif num_of_line > 4 and num_of_line < 73:
                                num = list(map(float, line.strip().split()))
                                # 坐标变换
                                x.append(float('%.7s' % str(num.__getitem__(0))))
                                y.append(float('%.7s' % str(num.__getitem__(1))))
                            else:
                                break
                            num_of_line = num_of_line + 1
                except Exception:
                    os.remove(self.txt_path)
                    print("该标签数据不完整，请重新运行本程序写入")
        return x, y

    def replaceLine(self, txt_path, lineNum, newLine):
        """
        指定行替换字符串
        :param txt_path: 替换文件路径
        :param newLine: 新替换文本
        :return:
        """
        lines = []
        with open(txt_path, 'r') as fr:
            linelist = fr.readlines()
            fr.close()
        for l in linelist:
            lines.append(l)
        # 替换当前行字符串    
        oldLine = str(lines[lineNum-1])
        lines[lineNum-1] = lines[lineNum-1].replace(oldLine, newLine)
        with open(txt_path, 'w') as fw:
            fw.writelines(lines)
            fw.close()

if __name__ == '__main__':
    input_image_root_path = "待标注图片目录路径"
    for parent, dirnames, filenames in os.walk(input_image_root_path):
        for filename in filenames:
            img_path = os.path.join(parent, filename)
            Point_Move(img_path)



