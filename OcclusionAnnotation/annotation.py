'''
人脸遮挡手动标注
'''

import sys
import os
from PIL import Image
import re
import matplotlib.pyplot as plt
import logging
import logging.handlers

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

def replaceLine(txt_path, lineNum, newLine):
    """
    指定行替换字符串
    :param txt_path: 替换文件路径
    :param lineNum: 替换行序号
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

def imgShowAndMark(img_path, label_txt_path, relaceLineNum):
    """
    指定图片提示标记
    :param img_path: 待标记图片路径
    :param img_txt:  待标记图片标签路径
    :param lineNum:  待标记行序号（可为空）
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

    if relaceLineNum != None:
        # 自定义输入属性
        lines = []
        with open(label_txt_path, 'r') as fr:
            linelist = fr.readlines()
            fr.close()
        for l in linelist:
            lines.append(l)
        newLine = myInput("请输入当前图片7遮挡属性，已标记属性为：" + str(lines[relaceLineNum - 1]))
        print("你输入的属性为，{}！".format(newLine).strip())
        # 替换对应标签文件指定行
        replaceLine(label_txt_path, relaceLineNum, str(img_path) + " " + newLine)
    else:
        newLine = myInput("请输入当前图片7遮挡属性")
        print("你输入的属性为，{}！".format(newLine).strip())
        with open(label_txt_path, "a") as ot:
            ot.write(newLine)
            ot.close()
    logging.info("已标记：" + str(img_path) + " 属性为：" + str(newLine).strip())
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
    num_of_line = 1
    with open(label_txt_path, 'r') as tt:
        while True:
            line = tt.readline()
            num = list(map(str, line.strip().split()))
            img_path = num.__getitem__(0)
            # 消重
            f = open('Face_data_mark.log', 'r')
            a = f.readlines()
            current_img_name = os.path.basename(img_path)
            print(current_img_name)
            # matchObj = re.search(current_img_name, "%s" % a, re.M | re.I)
            is_mark = False
            for c in a:
                if current_img_name.strip() in c:
                # if matchObj:
                    print(img_path + " 已标记过")
                    is_mark = True
            if is_mark is False:
                print("正在标记：" + str(img_path))
                imgShowAndMark(img_path, label_txt_path, num_of_line)

            num_of_line += 1

# 生成初始化标签文件
def addFaceOccLabel(img_root_path, output_txt):
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
                    ot.write(img_path + " 0 0 0 0 0 0 0" + "\n")


if __name__ == "__main__":
    # 标签文件
    output_label_txt_path = "./data/train/train.txt"
    # 运行标注工具
    MarkToolWithImg("wait_mark_image_root_path", output_label_txt_path)  # 标签文件不存在的属性手动标注
    MarkToolWithTxt(output_label_txt_path)  # 标签文件存在的属性手动标注
