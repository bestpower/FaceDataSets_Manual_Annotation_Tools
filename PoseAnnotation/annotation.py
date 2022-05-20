'''
人脸姿态手动标注
'''

import sys
import os
import re
import matplotlib.pyplot as plt
import logging
import logging.handlers

from PIL import Image


logging.FileHandler(filename='Face_data_mark.log', mode='a', encoding='utf-8')
logging.basicConfig(filename='Face_data_mark.log', filemode='a', level=logging.INFO)

def myInput(prompt):
    """
    终端输入内容
    :param prompt: 终端提示信息
    :return:
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    return sys.stdin.readline()

def replaceLine(txt_path, oldLine, newLine):
    """
    指定行替换字符串
    :param txt_path: 替换文件路径
    :param oldLine: 原替换文本
    :param newLine: 新替换文本
    :return:
    """

    global oldLinelist
    # oldLines = []
    newLines = []
    with open(txt_path, 'r') as fr:
        oldLinelist = fr.readlines()
        fr.close()
    # for l in linelist:
    #     oldLines.append(l)
    # 替换当前行字符串
    for line in oldLinelist:
        if oldLine in line:
            line = line.replace(oldLine, newLine)
        newLines.append(line)

    with open(txt_path, 'w') as fw:
        fw.writelines(newLines)
        fw.close()


def imgShowAndMark(img_path, label_txt_path, current_line):
    """
    指定图片提示标记
    :param img_path: 待标记图片路径
    :param img_txt:  待标记图片标签路径
    :param current_line: 当前标记对比内容
    :return:
    """

    # 显示待标记图片
    im = Image.open(img_path)
    plt.imshow(im)
    plt.xticks([])  # 去掉横坐标值
    plt.yticks([])  # 去掉纵坐标值
    plt.axis('off')
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.show()

    if current_line != None:
        # 获取待标注目标行原信息
        global linelist
        with open(label_txt_path, 'r') as fr:
            linelist = fr.readlines()
            fr.close()
        # 待标注行信息
        global oldLine
        for line in linelist:
            if img_path in line:
                oldLine = line

        # 根据对比信息标注新的属性值
        newLine = myInput("请输入当前图片姿态 Yaw Pitch Roll 属性，已标注属性提示为：" + str(current_line))
        print("你输入的属性值为，{}！".format(newLine).strip())
        # 用新标注行替换原标注行
        replaceLine(label_txt_path, oldLine, newLine)
    else:
        newLine = myInput("请输入当前图片姿态 Yaw Pitch Roll 属性")
        print("你输入的属性为，{}！".format(newLine).strip())
        with open(label_txt_path, "a") as ot:
            ot.write(newLine)
            ot.close()
    # 插入对应标签文件指定行
    logging.info("已标记为：" + str(newLine).strip())
    plt.close()

def MarkToolWithImg(wait_mark_image_root_path, output_label_txt_path):
    """
        根据图片标注并生成标签文件
        :param wait_mark_image_root_path: 待标记图片根目录路径
        :param output_label_txt_path:  输出标签路径
        :return:
    """
    for parent, dirnames, filenames in os.walk(wait_mark_image_root_path):
        for filename in filenames:
            img_path = os.path.join(parent, filename)
            # 消重
            f = open('Face_data_mark.log', 'rb')
            a = f.readlines()
            matchObj = re.search(filename, "%s" % a, re.M | re.I)
            if matchObj:
                print(img_path + " 已标记过")
            else:
                print("正在标记：" + str(img_path))
                imgShowAndMark(img_path, output_label_txt_path, None)

def MarkToolWithTxt(label_txt_path):
    """
        根据标签文件定位图片并更新标注
        :param label_txt_path:  已标注标签路径
        :return:
    """
    with open(label_txt_path, 'r') as tt:
        while True:
            try:
                line = tt.readline()
                num = list(map(str, line.strip().split()))
                # 获取图片路径
                img_path = num.__getitem__(0)
                # 过滤已标注的行
                with open('Face_data_mark.log', 'r') as fdm:
                    markedLines = fdm.readlines()
                    fdm.close()
                current_img_name = os.path.basename(img_path)
                print(current_img_name)
                is_mark = False
                for c in markedLines:
                    if current_img_name.strip() in c:
                        print(img_path + " 已标注过")
                        is_mark = True
                if is_mark is False:
                    print("正在标注：" + str(img_path))
                    imgShowAndMark(img_path, label_txt_path, line)
            except Exception as e:
                print("标注结束：" + str(e))
                break
        tt.close()

# 生成初始化标签文件
def addFacePoseLabel(img_root_path, output_txt):
    for parent, dirnames, filenames in os.walk(img_root_path):
        for filename in filenames:
            img_path = os.path.join(parent, filename)
            # 消重
            f = open(output_txt, 'r')
            a = f.readlines()
            matchObj = re.search(os.path.basename(filename), "%s" % a, re.M | re.I)
            if matchObj:
                print(img_path + " 已标记过")
            else:
                print("正在标记：" + str(img_path))
                with open(output_txt, "a") as ot:
                    ot.write(img_path + " 0 0 0" + "\n")


if __name__ == '__main__':
    # 标签文件
    output_label_txt_path = "./train.txt"
    # 运行标注工具
    MarkToolWithImg("./images", output_label_txt_path)
    # MarkToolWithTxt(output_label_txt_path)

    # addLabelFlag("./data/train/no_meet_train.txt")