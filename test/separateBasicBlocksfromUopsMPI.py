'''
Descripttion:
version:
Author: Shaojie Tan
Date: 2021-10-14 09:25:05
LastEditors: Shaojie Tan
LastEditTime: 2021-11-29 14:53:43
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

def extractBasicblockFullCommand(taskfilename,datafile,taskname):
    global skip_num,uopsFolder,blockFrequencyFolder
    num=1
    textes=[]
    binary_textes=[]
    uops_testes=[]
    tmp_inst_text=[]
    # tmp_full_inst_text=[]
    tmp_inst_binary=[]
    tmp_inst_binary_reverse=[]
    unique_inst=set()
    frequency = defaultdict(int)
    unique_block=set()
    frequencyBlock = defaultdict(int)
    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)
    line = 1

    fread = open(datafile, "r")
    num_file = sum([1 for i in open(datafile, "r")])
    print("文件名: ", fread.name)
    fwrite = open("../"+uopsFolder+"/"+taskfilename+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_rawBlock.log", "w")

    fread.seek(187, 0) # 跳掉开头

    matchers = readUopsTable()
    # print(matchers)
   # 筛选规则：
   # 去除b 和c开头的 和 nop
   # 如果其余代码总数大于 skip_num 将其缓存
    # lines=fread.readlines()
    # for line in track(lines,total=num_file):
    for line in tqdm(fread,total=num_file):
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
                textes.append(tmp_inst_text)
                binary_textes.append(tmp_inst_binary)

                tmp_uops_text=[]
                for tmp in tmp_inst_text:
                    tmp_uops_text.append(classify(str(tmp),matchers))
                uops_testes.append(tmp_uops_text)

                frequencyBlock[str(tmp_inst_text)] += 1
                unique_block.add(str(tmp_inst_text))

                unique_revBiblock.add(str(' '.join(tmp_inst_binary_reverse)))
                frequencyRevBiBlock[' '.join(tmp_inst_binary_reverse)] += 1

                for tmp_word in tmp_inst_text:
                    unique_inst.add(tmp_word)
                    frequency[tmp_word] += 1
                fwrite.writelines(str(tmp_inst_text)+"  "+str(tmp_uops_text)+" "+' '.join(tmp_inst_binary)+"\n")
                fwrite.writelines(' '.join(tmp_inst_binary_reverse)+"\n")
            tmp_inst_text=[]
            tmp_inst_binary=[]
            tmp_inst_binary_reverse=[]
    fwrite.close()
    fread.close()
    fwriteUops = open("../"+uopsFolder+"/"+taskfilename+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uops.log", "wb")
    pickle.dump(uops_testes, fwriteUops)
    fwriteUops.close()

    fwrite_uniqueInst = open("../"+uopsFolder+"/"+taskfilename+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueInst.log", "w")

    unique_uops=set()
    frequencyUops= defaultdict(int)
    # uniqueInst
    for uniqueInst in sorted(unique_inst):
        uops=classify(str(uniqueInst),matchers)
        fwrite_uniqueInst.writelines(str(uniqueInst)+" "+str(frequency[uniqueInst])+" "+uops+"\n")
        unique_uops.add(uops)
        frequencyUops[uops]+=frequency[uniqueInst]
    fwrite_uniqueInst.close()
    logging.debug(unique_inst)

    Totalwords=0
    for uniqueUops in sorted(unique_uops):
        Totalwords+=frequencyUops[uniqueUops]
    fwrite_uniqueUops = open("../"+uopsFolder+"/"+taskfilename+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueUops.log", "w")
    for uniqueUops in sorted(unique_uops):
        fwrite_uniqueUops.writelines(uniqueUops+" "+str(frequencyUops[uniqueUops])+" "+str(frequencyUops[uniqueUops]/Totalwords)+"%\n")
    fwrite_uniqueUops.close()

    fwriteblockfreq = open("../"+blockFrequencyFolder+"/"+str(taskname)+"_skip_"+str(skip_num)+".log", "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()

#     fwrite_blockfreq = open("../"+uopsFolder+"/"+taskfilename+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueBlockFreq.log", "w")
#     # block frequency
#     for tmp_text in sorted(unique_block):
#         fwrite_blockfreq.writelines(tmp_text+" "+str(frequencyBlock[tmp_text])+"\n")
#     fwrite_blockfreq.close()

    return [binary_textes,textes,unique_block,frequencyBlock,uops_testes]

# add features
# skip less 5 intrs blocks

def mpiProcess(task,wait2endQueue):
    for taskname in task.keys():
        datafile=task[taskname]
        taskfilename=taskname+"_skip_"+str(skip_num)
        print(taskfilename)
        checkFile(taskfilename)
        [binary_textes, texts,unique_block,frequencyBlock,uops]=extractBasicblockFullCommand(taskfilename,datafile,taskname)

        M = len(texts)
        M2 = len(uops)
        print('语料库载入完成，据统计，一共有 %d 篇文档与 %d uops' %( M , M2))
    wait2endQueue.put(task)
        # [lda,corpus_tfidf,num_topics,dictionary]=LDA(uops)
        # # # writeData("dictionary", dictionary)
        # # # writeData("corpus_tfidf",corpus_tfidf)
        # output(lda,corpus_tfidf,num_topics,dictionary)
        # writeOutput(lda,corpus_tfidf,num_topics,dictionary,binary_textes, texts,unique_block,frequencyBlock,uops)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING) # DEBUG or WARNING
    # [binary_textes, texts,unique_block,frequencyBlock]=extractBasicblock()

    # taskname="Eigen_MM"
    # datafile="../../../test/Eigen_MM.log"
    # taskname="test"
    # datafile="../test/test.log"
    # taskname="Eigen_10W"
    # datafile="../../../test/Eigen_MM_10W.log"
    # taskname="Eigen_100W"
    # datafile="../../../test/Eigen_MM_100W.log"
    # taskname="Eigen_1000W"
    # datafile="../../../test/Eigen_MM_1000W.log"
    # taskname="redis10M"
    # datafile="../../../test/redis10M.log"
    # taskname="redis1M"
    # datafile="../../../test/redis1M.log"
    # global taskname,datafile
    task={}
    # task["redis1M"]="../../../test/redis1M.log"
    # task["Eigen_10W"]="../../../test/Eigen_MM_10W.log"
    # task["Eigen_100W"]="../../../test/Eigen_MM_100W.log"
    # task["Eigen_1000W"]="../../../test/Eigen_MM_1000W.log"
    # task["gzip_full"]="../../../test/gzip_bhive_17M_full.log"
    # task["Eigen_full"]="../../../test/Eigen_MM.log"
    # task["redis_full"]="../../../test/redis_r1000_n1000_P16.log"
    # task["tensorflow_41Gdir_0000"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0000"
    # task["tensorflow_41Gdir_0001"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0001"
    # task["tensorflow_41Gdir_0002"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0002"
    # task["tensorflow_41Gdir_0003"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0003"
    # task["tensorflow_41Gdir_0004"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0004"
    # task["tensorflow_41Gdir_0005"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0005"
    # task["clang_harness_0000"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0000"
    # task["clang_harness_0001"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0001"
    # task["clang_harness_0002"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0002"
    # task["clang_harness_0003"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0003"
    # task["clang_harness_0004"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0004"
    # task["clang_harness_0005"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0005"
    # task["clang_harness_0006"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0006"
    # task["test100W_gzip_00"]="/home/shaojiemike/test/LDA_src/test100W_gzip_00"
    # task["test100W_gzip_01"]="/home/shaojiemike/test/LDA_src/test100W_gzip_01"
    # task["test100W_gzip_02"]="/home/shaojiemike/test/LDA_src/test100W_gzip_02"
    # task["test100W_gzip_03"]="/home/shaojiemike/test/LDA_src/test100W_gzip_03"
    # task["test100W_gzip_04"]="/home/shaojiemike/test/LDA_src/test100W_gzip_04"
    # task["test100W_gzip_05"]="/home/shaojiemike/test/LDA_src/test100W_gzip_05"
    # task["test100W_gzip_06"]="/home/shaojiemike/test/LDA_src/test100W_gzip_06"
    # rawTaskNum=44
    # rawTaskNamePrefix="MM_median_"
    # rawTaskPathPrefix="/home/shaojiemike/test/Eigen/MM_median_"

    rawTaskNum=48
    rawTaskNamePrefix="redis_r1000000_n2000000_P16_"
    rawTaskPathPrefix="/home/shaojiemike/test/redis/redis_r1000000_n2000000_P16_"
    for i in range(rawTaskNum):
        rawTaskName="{}{:02d}".format(rawTaskNamePrefix,i)
        rawTaskPath="{}{:02d}".format(rawTaskPathPrefix,i)
        task[rawTaskName]=rawTaskPath

    wait2endQueue =Queue()
    ProcessNum=16
    # taskNum need > ProcessNum
    taskRank=[]
    for taskname in task.keys():
        taskRank.append(taskname)
    taskNum=len(taskRank)
    for i in range(ProcessNum):
        startTaskNum=int(i*taskNum/ProcessNum)
        endTaskNum=int((i+1)*taskNum/ProcessNum)
        print("start end : {} {}".format(startTaskNum,endTaskNum))
        mpiTask={}
        for j in range(startTaskNum,endTaskNum):
            mpiTask[taskRank[j]]=task[taskRank[j]]
        p = Process(target=mpiProcess, args=(mpiTask,wait2endQueue))
        p.start()
    while wait2endQueue.qsize()<ProcessNum:
        print("wait2endQueue : {}".format(wait2endQueue.qsize()))
        sys.stdout.flush()
        time.sleep(5)
    print("Finished!")