#!/usr/bin/env python3
# encoding: utf-8
"""
@version: v1.0
@author: WESOFT
"""

import json
import logging.config
import os
import re
import time
from datetime import datetime

import cv2

from Common.CONST_j import CONST

PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))


def setup_logging(path=PATH('logging.json'), console=CONST.CONSOLE_PATH, error=CONST.ERROR_PATH):
    """
    设置日志
    :param path: 日志配置文件的路径
    :param console: 框架执行过程中日志的存储路径
    :param error: 框架执行过程中错误日志的存储路径
    :return:
    """
    with open(path, 'rt') as f:
        config = json.load(f)
    config['handlers']['info_file_handler']['filename'] = console
    config['handlers']['error_file_handler']['filename'] = error
    logging.config.dictConfig(config)


def get_execution_log(file, end_tag: str) -> str:
    """
    从日志文件的最后一行开始读取具体用例的执行日志
    :param file: 日志文件的路径
    :param end_tag: 结束读取的标志字符串
    :return: 执行日志
    """
    with open(file, encoding='utf-8') as f:
        all_line = f.readlines()
        all_line.reverse()
    content = ''
    for line in all_line:
        if re.match(end_tag, line):
            break
        else:
            content = line + content
    return content


def get_run_time():
    """
    获取当前时间
    :return: 当前时间的字符串，格式HH:MM:SS
    """
    current_time = time.strftime("%H:%M:%S", time.localtime())
    return current_time


def get_duration(start_time: str, end_time: str) -> int:
    """
    获取两个时间的差值(秒)
    :param start_time: 起始时间的字符串，格式HH:MM:SS
    :param end_time: 结束时间的字符串，格式HH:MM:SS
    :return:
    """
    st = datetime.strptime(start_time, "%H:%M:%S")
    et = datetime.strptime(end_time, "%H:%M:%S")
    return (et - st).seconds


def lists_compare(list1: list, list2: list):
    """
    判断两个列表是否存在独有的值
    :param list1: 列表1
    :param list2: 列表2
    :return: 列表1有列表2没有的值：返回1和列表1独有的值；列表2有列表1没有的值，返回2和列表2独有的值；列表1和2都有独有的值，返回3和列表1/2独有的值；列表1/2没有不同的值，返回4和空列表
    """
    list1_diff = list(set(list1).difference(set(list2)))
    list2_diff = list(set(list2).difference(set(list1)))
    if list1_diff:
        if list2_diff:
            return 3, list1_diff, list2_diff
        return 1, list1_diff
    if list2_diff:
        return 2, list2_diff
    return 4, []


def cut_text(text: str, length: int) -> list:
    """
    @Elden on 4/1/2019
    按长度等分字符串
    :param text: 需要被等分的字符串
    :param length: 每隔多长做等分
    :return: 等分后的字符串列表
    """
    textarr = re.findall('.{' + str(length) + '}', text)
    textarr.append(text[(len(textarr) * length):])
    return textarr


def hex2str(hex_text: str, hex_length: int):
    """
    @Elden on 4/1/2019
    将一个由16进制表示的字符串转换回以字母表示的字符串
    :param hex_text: 16进制表示的字符串
    :param hex_length: 每个16进制字符的长度
    :return: 返回以字母表示的字符串
    """
    try:
        char_list = cut_text(hex_text, hex_length)
        converted = ""
        for c in char_list:
            if c != "":
                converted = converted + chr(int(c, 16))
        return converted
    except Exception as msg:
        print(msg)


def str2hex(text: str):
    """
    @Elden on 4/1/2019
    将一个字符串转换回以由16进制编码表示的字符串
    :param text: 要转换的字符串
    :return: 以16进制编码表示的字符串
    """
    try:
        converted = ""
        for t in text:
            if t is not None:
                converted = converted + hex(ord(t))
        return converted
    except Exception as msg:
        print(msg)


def rc4(text: str, key='default-key', md5=False):
    """
    @Elden on 4/1/2019 RC4加密解密方法
    :param text: 要加密的字符串 / 要解密的字符串
    :param key:  密钥
    :param md5:  是否需要先将密钥使用md5加密后再用来加密解密
    :return: 加密或者解密后的字符串
    """
    try:
        if md5 is True:
            import hashlib
            # 取长度固定为32的MD5摘要值作为密钥，从而方便处理
            # 要注意hashlib库求取文本md5的值时文本必须为utf-8编码
            key = hashlib.md5(key.encode('utf-8')).hexdigest()

        result = ''

        # 1. 初始化S-box
        box = list(range(256))  # 将数字0 - 255按顺序放入S-box

        # 将文本转换成编码, Python默认的编码方式为utf-8编码
        # 而下面存放的编码格式默认为10进制数字
        key_code = list()
        for k in key:
            key_code.append(ord(k))

        # 由于VBA处理字符串时会在文本最后放结束符(二进制0),所以为了兼容VBA处理过的文本
        # 这里需要在字符串后加0
        key_code.append(0)
        key_len = len(key_code)

        # 2. 使用key来混淆S-box的顺序
        j = 0
        for i in range(256):
            swap_code = key_code[i % key_len]  # 这里的作用是使key code循环使用
            j = (j + box[i] + swap_code) & 255
            # 交换S-box中的元素
            box[i], box[j] = box[j], box[i]

        # 3. 加密明文
        i = j = 0
        for element in text:
            #  求取加密字节
            i = (i + 1) & 255
            j = (j + box[i]) & 255
            box[i], box[j] = box[j], box[i]
            nextbyte = box[(box[i] + box[j]) & 255]

            #  将文本中的一个字符编码化
            code = ord(element)
            k = code ^ nextbyte  # 使用加密字节混淆明文,得到密文
            result += chr(k)

        return result
    except Exception as msg:
        print(msg)


def line_break(text: str, every: int):
    """
    为长字符串插入换行符
    :param text: 原字符串
    :param every: 每*个字符插入一个换行符
    :return: 增加换行符后的新字符串
    """
    try:
        return re.sub("(.{%d})" % every, "\\1\n", text, 0, re.DOTALL) + '\n'
    except Exception as msg:
        print(msg)


def get_pictures(filepath: str):
    """
    获取.jpg或.png的图片
    :param filepath: 图片路径(可以是目录或文件)
    :return: .jpg或.png的图片路径
    """
    picture = []

    # 判断路径是否存在
    if not os.path.exists(filepath):
        logging.exception('没有找到{0}文件'.format(filepath))
        return picture
    # 判断路径是目录或文件
    if os.path.isdir(filepath):
        # 循环目录中的文件获取.jpg或.png的图片
        for file in os.listdir(filepath):
            file_path = os.path.join(filepath, file)
            if os.path.isdir(file_path):
                get_pictures(file_path)
            elif os.path.splitext(file_path)[1] in ('.jpg', '.png'):
                picture.append(file_path)
    elif os.path.isfile(filepath):
        if os.path.splitext(filepath)[1] in ('.jpg', '.png'):
            picture.append(os.path.join(filepath))
    return picture


def resize_picture(path: str, size: tuple = (118, 77)):
    """
    调整图片大小
    :param path: 图片路径
    :param size: 调整的大小,宽和高
    :return:
    """
    try:
        img = cv2.imread(path)
        # 获取图片大小
        imgsize = img.shape
        # 如果宽或者高不等于指定大小，则resized
        if imgsize[0] != size[1] or imgsize[1] != size[0]:
            resized = cv2.resize(img, size, interpolation=cv2.INTER_CUBIC)
            filename = os.path.basename(path)
            cv2.imwrite(filename, resized)
    except Exception as msg:
        logging.exception('不能变更图片:{0} 的大小'.format(path))
