'''
Descripttion:
version:
Author: Shaojie Tan
Date: 2021-10-14 09:25:05
LastEditors: Shaojie Tan
LastEditTime: 2021-12-23 16:55:22
'''
import numpy as np
from gensim import corpora, models, similarities
import time
import matplotlib.pyplot as plt
from pylab import *
import logging
from collections import defaultdict
import pickle
import re
import os
from rich.progress import track
from tqdm import *
import  time
from multiprocessing import Process, Queue



num_topics=6
skip_num=2
uopsFolder="uops"
classFolder="BasicBlock"
blockFrequencyFolder="blockFrequency"

# 文件交互说明：
# 读 ../../../test/Eigen_MM_10W.log
# ../arm2uops/UopsTable.txt

def binaryReverse(string):
    return string[6:8]+string[4:6]+string[2:4]+string[0:2]
def checkFile(taskfilename):
    global classFolder,uopsFolder
    uopsPath=os.getcwd()[:-4]+"/"+uopsFolder+"/"+taskfilename
    mkdir(uopsPath)
    classPath=os.getcwd()[:-4]+"/"+classFolder+"/"+taskfilename
    mkdir(classPath)
    # blockFrequencyPath=os.getcwd()[:-4]+"/"+blockFrequencyFolder+"/"+taskfilename
    # mkdir(blockFrequencyPath)
    print(classPath)

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
		print("---  new folder...  ---")
	else:
		print("---  There is this folder!  ---")

def writeData(filename,data): # for test
    global uopsFolder
    fwrite = open("../"+uopsFolder+"/"+taskfilename+"/"+str(taskname)+"_"+str(filename)+".log", "w")
    for tmp in data:
        fwrite.writelines(str(tmp)+"\n")
    fwrite.close()

def readUopsTable():
    data = {}
    with open("../arm2uops/UopsTable.txt", 'r') as f:#with语句自动调用close()方法
        line = f.readline()
        while line:
            # data[line[0:6]]=line[8:-1]
            data[line[8:-1]]=line[0:6]
            line = f.readline()
    return data #返回数据为双列表形式

def classify(journaltext,matchers):
    # matchers = {"p45->2": "^add    %q[0-9]*", "p01->1": "^add    %[swx]"}
    # for category in sorted(matchers.keys()):
    #     if re.match(matchers[category], journaltext):
    #         return category
    for regexText in sorted(matchers.keys()):
        if re.match(regexText,journaltext):
            return matchers[regexText]
    return "UNKOWN" # or you can "return None"

def extractBasicblockFullCommand(taskfilename,datafile,taskname,rank):
    global skip_num,uopsFolder,blockFrequencyFolder
    num=1
    textNum=0
    uops_testes=[]
    tmp_inst_text=[]
    tmp_inst_binary=[]
    tmp_inst_binary_reverse=[]
    unique_block=set()
    frequencyBlock = defaultdict(int)
    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)
    line = 1

    fread = open(datafile, "r")
    val = os.popen("wc -l {}".format(datafile))
    list = val.readlines()
    regexResult=re.search("^([0-9]*) ",list[0])
    num_file=int(regexResult.group(1))
    print("文件名: {} {}".format(fread.name,num_file))


    matchers = readUopsTable()
    # print(matchers)
   # 筛选规则：
   # 去除b 和c开头的 和 nop
   # 如果其余代码总数大于 skip_num 将其缓存
    # lines=fread.readlines()
    # for line in track(lines,total=num_file):
    for line in tqdm(fread,total=num_file,desc=str("{:2d}".format(rank))):
        # time.sleep(0.5)
        logging.debug("读取的数据为: %s" % (line))
        logging.debug(line[13:17])
        if line[13:17]=="0000" and line[42:43]!="b" and line[42:43]!="c" \
            and line[42:45]!="nop" and line[42:45]!="dmb" and line[42:45]!="msr"\
            and line[42:45]!="mrs" and line[42:45]!="svc" and line[42:45]!="sys"\
            and line[42:45]!="isb" and line[42:45]!="ret" and line[42:45]!="tbz"\
            and line[42:45]!="tbn": #去除b 和c开头的
            # tmp_inst_text.append(line[42:-1])

            tmp_inst_text.append(line[42:-1])# 去除 \n
                # tmp_full_inst_text.append(line[42:])
            tmp_inst_binary.append(line[31:39])
            tmp_inst_binary_reverse.append(binaryReverse(line[31:39]))
        elif line[13:17]=="writ" or line[13:17]=="read" or line[42:43]=="b":
            if len(tmp_inst_text) > skip_num:
                # textes.append(tmp_inst_text)
                textNum+=1
                # binary_textes.append(tmp_inst_binary)

                # tmp_uops_text=[]
                # for tmp in tmp_inst_text:
                #     tmp_uops_text.append(classify(str(tmp),matchers))
                # uops_testes.append(tmp_uops_text)

                # frequencyBlock[str(tmp_inst_text)] += 1
                # unique_block.add(str(tmp_inst_text))

                unique_revBiblock.add(str(' '.join(tmp_inst_binary_reverse)))
                frequencyRevBiBlock[' '.join(tmp_inst_binary_reverse)] += 1

                # for tmp_word in tmp_inst_text:
                #     unique_inst.add(tmp_word)
                #     frequency[tmp_word] += 1
                # fwrite.writelines(str(tmp_inst_text)+"  "+str(tmp_uops_text)+" "+' '.join(tmp_inst_binary)+"\n")
                # fwrite.writelines(' '.join(tmp_inst_binary_reverse)+"\n")
            tmp_inst_text=[]
            tmp_inst_binary=[]
            tmp_inst_binary_reverse=[]
    # fwrite.close()
    fread.close()


    fwriteblockfreq = open("../"+blockFrequencyFolder+"/"+str(taskname)+"_skip_"+str(skip_num)+".log", "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()


    return [[],textNum,unique_block,frequencyBlock,uops_testes]

# add features
# skip less 5 intrs blocks




if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING) # DEBUG or WARNING
    task={}
    # rawTaskNum=2
    # rawTaskNamePrefix="MM_median_"
    # rawTaskPathPrefix="/home/shaojiemike/test/Eigen/MM_median_"
    # for i in range(rawTaskNum):
    #     rawTaskName="{}{:02d}".format(rawTaskNamePrefix,i)
    #     rawTaskPath="{}{:02d}".format(rawTaskPathPrefix,i)
    #     task[rawTaskName]=rawTaskPath

    # rawTaskNum=48
    # rawTaskNamePrefix="redis_r1000000_n2000000_P16_"
    # rawTaskPathPrefix="/home/shaojiemike/test/redis/redis_r1000000_n2000000_P16_"
    # for i in range(rawTaskNum):
    #     rawTaskName="{}{:02d}".format(rawTaskNamePrefix,i)
    #     rawTaskPath="{}{:02d}".format(rawTaskPathPrefix,i)
    #     task[rawTaskName]=rawTaskPath

    [binary_textes, textNum,unique_block,frequencyBlock,uops]=extractBasicblockFullCommand(taskfilename,datafile,taskname,rank)

    M = textNum
    M2 = len(uops)
    print('语料库载入完成，据统计，一共有 %d 篇文档与 %d uops' %( M , M2))
    
    print("Finished!")