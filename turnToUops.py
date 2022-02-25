'''
Descripttion: 
version: 
Author: Shaojie Tan
Date: 2021-11-13 18:35:48
LastEditors: Shaojie Tan
LastEditTime: 2021-11-16 15:51:12
'''
import numpy as np
from gensim import corpora, models, similarities
import time
import matplotlib.pyplot as plt
from pylab import *
import logging
from collections import defaultdict
import re
import pickle


# taskname="Eigen_MM"
# datafile="../../../test/Eigen_MM.log"
# taskname="test"
# datafile="../test/test.log"
taskname="Eigen_10W"
datafile="../../../test/Eigen_MM_10W.log"
# taskname="Eigen_100W"
# datafile="../../../test/Eigen_MM_100W.log"
# taskname="Eigen_1000W"
# datafile="../../../test/Eigen_MM_1000W.log"
num_topics = 2
skip_num=2
saveFolder="uops"

def writeData(filename,data):
    global saveFolder
    fwrite = open("../"+saveFolder+"/"+str(taskname)+"_"+str(filename)+".log", "w")
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

def extractBasicblockFullCommand():
    global skip_num,datafile,saveFolder
    num=1
    textes=[]
    binary_textes=[]
    uops_testes=[]
    tmp_inst_text=[]
    # tmp_full_inst_text=[]
    tmp_inst_binary=[]
    unique_inst=set()   
    frequency = defaultdict(int)
    unique_block=set()
    frequencyBlock = defaultdict(int)
    line = 1

    fread = open(datafile, "r")
    print("文件名: ", fread.name)
    fwrite = open("../"+saveFolder+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_rawBlock.log", "w")
    fread.seek(187, 0) # 跳掉开头
   
    matchers = readUopsTable()
    print(matchers)
   # 筛选规则：
   # 去除b 和c开头的 和 nop
   # 如果其余代码总数大于 skip_num 将其缓存
    while line:
        line = fread.readline()
        logging.debug("读取的数据为: %s" % (line))
        logging.debug(line[13:17])
        if line[13:17]=="0000" and line[42:43]!="b" and line[42:43]!="c" \
            and line[42:45]!="nop" and line[42:45]!="dmb" and line[42:45]!="msr"\
            and line[42:45]!="mrs" and line[42:45]!="svc" and line[42:45]!="sys"  : #去除b 和c开头的
            # tmp_inst_text.append(line[42:-1])
            
            tmp_inst_text.append(line[42:-1])# 去除 \n   
                # tmp_full_inst_text.append(line[42:])
            tmp_inst_binary.append(line[31:39])
        elif line[13:17]=="writ" or line[13:17]=="read" or line[42:43]=="b":
            if len(tmp_inst_text) > skip_num:
                textes.append(tmp_inst_text)   
                binary_textes.append(tmp_inst_binary)            
                # fwrite.writelines(str(tmp_inst_text)+"  "+' '.join(tmp_inst_binary)+"\n")
                tmp_uops_text=[]
                for tmp in tmp_inst_text:                   
                    tmp_uops_text.append(classify(str(tmp),matchers))
                uops_testes.append(tmp_uops_text)
                frequencyBlock[str(tmp_inst_text)] += 1
                unique_block.add(str(tmp_inst_text))
                for tmp_word in tmp_inst_text:
                    unique_inst.add(tmp_word)
                    frequency[tmp_word] += 1
            tmp_inst_text=[]
            tmp_inst_binary=[]
    fwrite.close()
    fread.close()
    fwriteUops = open("../"+saveFolder+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uops.log", "wb")  
    pickle.dump(uops_testes, fwriteUops)
    fwriteUops.close()

    fwrite_uniqueInst = open("../"+saveFolder+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueInst.log", "w")
   
    # uniqueInst
    for uniqueInst in sorted(unique_inst):
        uops=classify(str(uniqueInst),matchers)
        fwrite_uniqueInst.writelines(str(uniqueInst)+" "+str(frequency[uniqueInst])+" "+uops+"\n")
    fwrite_uniqueInst.close()
    logging.debug(unique_inst)

#     fwrite_blockfreq = open("../"+saveFolder+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueBlockFreq.log", "w")
#     # block frequency
#     for tmp_text in sorted(unique_block):
#         fwrite_blockfreq.writelines(tmp_text+" "+str(frequencyBlock[tmp_text])+"\n")
#     fwrite_blockfreq.close()

    return [binary_textes,textes,unique_block,frequencyBlock]


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING) # DEBUG or WARNING
    # [binary_textes, texts,unique_block,frequencyBlock]=extractBasicblock()
    [binary_textes, texts,unique_block,frequencyBlock]=extractBasicblockFullCommand()
    logging.debug(texts)

    M = len(texts)
    print('语料库载入完成，据统计，一共有 %d 篇文档' % M)