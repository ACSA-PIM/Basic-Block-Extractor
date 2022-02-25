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
def checkFile():
    global taskfilename,classFolder,uopsFolder
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

def extractBasicblockFullCommand():
    global skip_num,datafile,uopsFolder,blockFrequencyFolder
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

def LDA(texts):
    global num_topics
    # build the dictionary for texts
    dictionary = corpora.Dictionary(texts)
    dict_len = len(dictionary)
    # transform the whole texts to sparse vector
    corpus = [dictionary.doc2bow(text) for text in texts]
    # create a transformation, from initial model to tf-idf model
    corpus_tfidf = models.TfidfModel(corpus)[corpus]
    print('现在开始训练LDA模型：---')
    t_start = time.time()
    # create a transformation, from tf-idf model to lda model
    lda = models.LdaModel(corpus_tfidf, num_topics=num_topics, id2word=dictionary,
        alpha=1/6, eta=1/13, minimum_probability=0.001, update_every = 1, chunksize = 100, passes = 1)
    print('LDA模型完成，耗时 %.3f 秒\n\n' % (time.time() - t_start))
    # writeData("corpus",corpus)
    return [lda,corpus_tfidf,num_topics,dictionary]

def output(lda,corpus_tfidf,num_topics,dictionary):
    # 打印前9个文档的主题
    num_show_topic = 9  # 每个文档显示前几个主题
    fwrite = open("../"+str(classFolder)+"/"+taskfilename+"/"+str(taskname)+"_classTest.log", "w")
    print('下面，显示前9个文档的主题分布：')
    fwrite.writelines('下面，显示前9个文档的主题分布：')
    doc_topics = lda.get_document_topics(corpus_tfidf)  # 所有文档的主题分布
    for i in range(9):
        topic = np.array(doc_topics[i])
        # writeData("topic"+str(i),topic)
        topic_distribute = np.array(topic[:, 1])
        topic_idx = list(topic_distribute)
        print('\n第%d个文档的 %d 个主题分布概率分别为：' % (i, num_show_topic))
        print(topic_idx)
        fwrite.writelines('\n第%d个文档的 %d 个主题分布概率分别为：' % (i, num_show_topic))
        fwrite.writelines(str(topic_idx))

    print('\n下面，显示每个主题的词分布：')
    fwrite.writelines('\n下面，显示每个主题的词分布：')
    num_show_term = 7   # 每个主题下显示几个词
    for topic_id in range(num_topics):
        print('\n第%d个主题的词与概率如下：\t' % topic_id)
        fwrite.writelines('\n第%d个主题的词与概率如下：\t' % topic_id)
        term_distribute_all = lda.get_topic_terms(topicid=topic_id)
        term_distribute = term_distribute_all[:num_show_term]
        term_distribute = np.array(term_distribute)
        term_id = term_distribute[:, 0].astype(np.int)
        print('词：\n', end='')
        fwrite.writelines('词：\n')
        for t in term_id:
            print(dictionary.id2token[t], end='\n')
            fwrite.writelines(str(dictionary.id2token[t])+"\n")
        print('概率：\t\n', term_distribute[:, 1])
        fwrite.writelines('概率：\t\n'+str(term_distribute[:, 1]))
    fwrite.close()
def writeOutput(lda,corpus_tfidf,num_topics,dictionary,binary_textes, texts,unique_block,frequencyBlock,uops):
    global classFolder
    fwrite = open("../"+str(classFolder)+"/"+taskfilename+"/"+str(taskname)+"_writeOutput_raw.log", "w")
    fwriteNumclass = openNumtopic()
    frequency = defaultdict(int)
    doc_topics = lda.get_document_topics(corpus_tfidf)  # 所有文档的主题分布
    for i in range(len(texts)):
        topic = np.array(doc_topics[i])
        topic_distribute = np.array(topic[:, 1])
        topic_idx = list(topic_distribute)
        max_value = max(topic_idx)
        max_index = topic_idx.index(max_value)
        frequency[max_index]+=1
        fwrite.writelines(str(texts[i])+str(uops[i])+"  "+' '.join(binary_textes[i])+" Class"+str(max_index)+"\n")
        if str(texts[i]) in unique_block:
            unique_block.remove(str(texts[i]))
            fwriteNumclass[max_index].writelines(str(texts[i])+str(uops[i])+"  "+' '.join(binary_textes[i])+" Class"+str(max_index)+" frequency "+str(frequencyBlock[str(texts[i])])+"\n")
    closeNumtopic(fwriteNumclass)
    fwrite.close()
    fwriteClass = open("../"+str(classFolder)+"/"+taskfilename+"/"+str(taskname)+"_class.log", "w")
    for i in range(num_topics):
        fwriteClass.writelines("Class"+str(i)+": "+str(frequency[i])+" "+str(frequency[i]/len(texts))+"%\n")
    fwriteClass.writelines("Total block numbers: "+str(len(texts)))
    fwriteClass.close()

def openNumtopic():
    global num_topics,classFolder
    fwriteclass = []
    for i in range(num_topics):
        fwriteclass.append(open("../"+str(classFolder)+"/"+taskfilename+"/"+str(taskname)+"_writeOutput_class"+str(i)+".log", "w"))
    return fwriteclass

def closeNumtopic(fwriteNumclass):
    global num_topics
    for i in range(num_topics):
        fwriteNumclass[i].close()

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
    global taskname,datafile
    task={}
    # task["redis1M"]="../../../test/redis1M.log"
    # task["Eigen_10W"]="../../../test/Eigen_MM_10W.log"
    # task["Eigen_100W"]="../../../test/Eigen_MM_100W.log"
    # task["Eigen_1000W"]="../../../test/Eigen_MM_1000W.log"
    # task["gzip_full"]="../../../test/gzip_bhive_17M_full.log"
    # task["Eigen_full"]="../../../test/Eigen_MM.log"
    # task["redis_full"]="../../../test/redis_r1000_n1000_P16.log"
    task["tensorflow_41Gdir_0000"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0000"
    task["tensorflow_41Gdir_0001"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0001"
    task["tensorflow_41Gdir_0002"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0002"
    task["tensorflow_41Gdir_0003"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0003"
    task["tensorflow_41Gdir_0004"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0004"
    task["tensorflow_41Gdir_0005"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0005"
    task["tensorflow_41Gdir_0006"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0006"
    task["tensorflow_41Gdir_0007"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0007"
    task["tensorflow_41Gdir_0008"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0008"
    task["tensorflow_41Gdir_0009"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0009"
    task["tensorflow_41Gdir_0010"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0010"
    task["tensorflow_41Gdir_0011"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0011"
    task["tensorflow_41Gdir_0012"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0012"
    task["tensorflow_41Gdir_0013"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0013"
    task["tensorflow_41Gdir_0014"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0014"
    task["tensorflow_41Gdir_0015"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0015"
    task["tensorflow_41Gdir_0016"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0016"
    task["tensorflow_41Gdir_0017"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0017"
    task["tensorflow_41Gdir_0018"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0018"
    task["tensorflow_41Gdir_0019"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0019"
    task["tensorflow_41Gdir_0020"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0020"
    task["tensorflow_41Gdir_0021"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0021"
    task["tensorflow_41Gdir_0022"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0022"
    task["tensorflow_41Gdir_0023"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0023"
    task["tensorflow_41Gdir_0024"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0024"
    task["tensorflow_41Gdir_0025"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0025"
    task["tensorflow_41Gdir_0026"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0026"
    task["tensorflow_41Gdir_0027"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0027"
    task["tensorflow_41Gdir_0028"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0028"
    task["tensorflow_41Gdir_0029"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0029"
    task["tensorflow_41Gdir_0030"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0030"
    task["tensorflow_41Gdir_0031"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0031"
    task["tensorflow_41Gdir_0032"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0032"
    task["tensorflow_41Gdir_0033"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0033"
    task["tensorflow_41Gdir_0034"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0034"
    task["tensorflow_41Gdir_0035"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0035"
    task["tensorflow_41Gdir_0036"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0036"
    task["tensorflow_41Gdir_0037"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0037"
    task["tensorflow_41Gdir_0038"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0038"
    task["tensorflow_41Gdir_0039"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0039"
    task["tensorflow_41Gdir_0040"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0040"
    task["tensorflow_41Gdir_0041"]="/home/shaojiemike/test/tensorflow/tensorflow_41Gdir_0041"
    # task["clang_harness_0000"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0000"
    # task["clang_harness_0001"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0001"
    # task["clang_harness_0002"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0002"
    # task["clang_harness_0003"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0003"
    # task["clang_harness_0004"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0004"
    # task["clang_harness_0005"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0005"
    # task["clang_harness_0006"]="/home/shaojiemike/test/clangBenchmark/clang_harness_0006"

    for taskname in task.keys():
        datafile=task[taskname]
        taskfilename=taskname+"_skip_"+str(skip_num)
        print(taskfilename)
        checkFile()
        [binary_textes, texts,unique_block,frequencyBlock,uops]=extractBasicblockFullCommand()

        M = len(texts)
        M2 = len(uops)
        print('语料库载入完成，据统计，一共有 %d 篇文档与 %d uops' %( M , M2))
        # [lda,corpus_tfidf,num_topics,dictionary]=LDA(uops)
        # # # writeData("dictionary", dictionary)
        # # # writeData("corpus_tfidf",corpus_tfidf)
        # output(lda,corpus_tfidf,num_topics,dictionary)
        # writeOutput(lda,corpus_tfidf,num_topics,dictionary,binary_textes, texts,unique_block,frequencyBlock,uops)

