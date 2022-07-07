'''
Descripttion:
version:
Author: Shaojie Tan
Date: 2021-10-14 09:25:05
LastEditors: Shaojie Tan
LastEditTime: 2021-11-13 18:33:25
'''
import numpy as np
from gensim import corpora, models, similarities
import time
import matplotlib.pyplot as plt
from pylab import *
import logging
from collections import defaultdict

skip_num=2
# taskname="Eigen_MM"
# datafile="../../../test/Eigen_MM.log"
taskname="test"
datafile="../test/test.log"
num_topics = 2

def writeData(filename,data):
    fwrite = open("../BasicBlock/"+str(taskname)+"_"+str(filename)+".log", "w")
    for tmp in data:
        fwrite.writelines(str(tmp)+"\n")
    fwrite.close()


# add features
# skip less 5 intrs blocks
def extractBasicblock():
    global skip_num,datafile
    num=1
    textes=[]
    binary_textes=[]
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
    fwrite = open("../BasicBlock/"+str(taskname)+"_skip_"+str(skip_num)+"_rawBlock.log", "w")
    # fwrite_full = open("../BasicBlock/Full"+str(taskname)+"_skip_"+str(skip_num)+"_rawBlock.log", "w")  
    fread.seek(187, 0) # 跳掉开头
   
   # 筛选规则：
   # 去除b 和c开头的 和 nop
   # 如果其余代码总数大于 skip_num 将其缓存
    while line:
        line = fread.readline()
        logging.debug("读取的数据为: %s" % (line))
        logging.debug(line[13:17])
        if line[13:17]=="0000" and line[42:43]!="b" and line[42:43]!="c": #去除b 和c开头的
            # tmp_inst_text.append(line[42:-1])
            if line[42:45]=="nop":
                tmp_inst_text.append("nop  ")  
            else:
                tmp_inst_text.append(line[42:47])   
                # tmp_full_inst_text.append(line[42:])
            tmp_inst_binary.append(line[31:39])
        elif line[13:17]=="writ" or line[13:17]=="read" or line[42:43]=="b":
            if len(tmp_inst_text) > skip_num:
                textes.append(tmp_inst_text)   
                binary_textes.append(tmp_inst_binary)            
                fwrite.writelines(str(tmp_inst_text)+"  "+' '.join(tmp_inst_binary)+"\n")
                frequencyBlock[str(tmp_inst_text)] += 1
                unique_block.add(str(tmp_inst_text))
                for tmp_word in tmp_inst_text:
                    unique_inst.add(tmp_word)
                    frequency[tmp_word] += 1
            tmp_inst_text=[]
            tmp_inst_binary=[]
    fwrite.close()
    fread.close()

    fwrite_uniqueInst = open("../BasicBlock/"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueInst.log", "w")
   
    # uniqueInst
    for uniqueInst in sorted(unique_inst):
        fwrite_uniqueInst.writelines(str(uniqueInst)+" "+str(frequency[uniqueInst])+"\n")
    fwrite_uniqueInst.close()
    logging.debug(unique_inst)

    fwrite_blockfreq = open("../BasicBlock/"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueBlockFreq.log", "w")
    # block frequency
    for tmp_text in sorted(unique_block):
        fwrite_blockfreq.writelines(tmp_text+" "+str(frequencyBlock[tmp_text])+"\n")
    fwrite_blockfreq.close()

    return [binary_textes,textes,unique_block,frequencyBlock]

def extractBasicblockFullCommand():
    global skip_num,datafile
    num=1
    textes=[]
    binary_textes=[]
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
    fwrite = open("../BasicBlock/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_rawBlock.log", "w") 
    fread.seek(187, 0) # 跳掉开头
   
   # 筛选规则：
   # 去除b 和c开头的 和 nop
   # 如果其余代码总数大于 skip_num 将其缓存
    while line:
        line = fread.readline()
        logging.debug("读取的数据为: %s" % (line))
        logging.debug(line[13:17])
        if line[13:17]=="0000" and line[42:43]!="b" and line[42:43]!="c": #去除b 和c开头的
            # tmp_inst_text.append(line[42:-1])
            if line[42:45]=="nop":
                tmp_inst_text.append("nop  ")  
            else:
                tmp_inst_text.append(line[42:-1])# 去除 \n   
                # tmp_full_inst_text.append(line[42:])
            tmp_inst_binary.append(line[31:39])
        elif line[13:17]=="writ" or line[13:17]=="read" or line[42:43]=="b":
            if len(tmp_inst_text) > skip_num:
                textes.append(tmp_inst_text)   
                binary_textes.append(tmp_inst_binary)            
                fwrite.writelines(str(tmp_inst_text)+"  "+' '.join(tmp_inst_binary)+"\n")
                frequencyBlock[str(tmp_inst_text)] += 1
                unique_block.add(str(tmp_inst_text))
                for tmp_word in tmp_inst_text:
                    unique_inst.add(tmp_word)
                    frequency[tmp_word] += 1
            tmp_inst_text=[]
            tmp_inst_binary=[]
    fwrite.close()
    fread.close()

    fwrite_uniqueInst = open("../BasicBlock/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueInst.log", "w")
   
    # uniqueInst
    for uniqueInst in sorted(unique_inst):
        fwrite_uniqueInst.writelines(str(uniqueInst)+" "+str(frequency[uniqueInst])+"\n")
    fwrite_uniqueInst.close()
    logging.debug(unique_inst)

    fwrite_blockfreq = open("../BasicBlock/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uniqueBlockFreq.log", "w")
    # block frequency
    for tmp_text in sorted(unique_block):
        fwrite_blockfreq.writelines(tmp_text+" "+str(frequencyBlock[tmp_text])+"\n")
    fwrite_blockfreq.close()

    return [binary_textes,textes,unique_block,frequencyBlock]

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
    print('下面，显示前9个文档的主题分布：')
    doc_topics = lda.get_document_topics(corpus_tfidf)  # 所有文档的主题分布
    for i in range(9):
        topic = np.array(doc_topics[i])
        # writeData("topic"+str(i),topic)
        topic_distribute = np.array(topic[:, 1])
        topic_idx = list(topic_distribute)
        print('第%d个文档的 %d 个主题分布概率分别为：' % (i, num_show_topic))
        print(topic_idx)

    print('\n下面，显示每个主题的词分布：')
    num_show_term = 7   # 每个主题下显示几个词
    for topic_id in range(num_topics):
        print('第%d个主题的词与概率如下：\t' % topic_id)
        term_distribute_all = lda.get_topic_terms(topicid=topic_id)
        term_distribute = term_distribute_all[:num_show_term]
        term_distribute = np.array(term_distribute)
        term_id = term_distribute[:, 0].astype(np.int)
        print('词：\n', end='')
        for t in term_id:
            print(dictionary.id2token[t], end='\n')
        print('\n概率：\t', term_distribute[:, 1])
def writeOutput(lda,corpus_tfidf,num_topics,dictionary,binary_textes, texts,unique_block,frequencyBlock):
    fwrite = open("../BasicBlock/"+str(taskname)+"_writeOutput_raw.log", "w")
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
        fwrite.writelines(str(texts[i])+"  "+' '.join(binary_textes[i])+" Class"+str(max_index)+"\n")
        if str(texts[i]) in unique_block:
            unique_block.remove(str(texts[i]))
            fwriteNumclass[max_index].writelines(str(texts[i])+"  "+' '.join(binary_textes[i])+" Class"+str(max_index)+" frequency "+str(frequencyBlock[str(texts[i])])+"\n")
    closeNumtopic(fwriteNumclass)
    fwrite.close()
    fwriteClass = open("../BasicBlock/"+str(taskname)+"_class.log", "w")
    for i in range(num_topics):
        fwriteClass.writelines("Class"+str(i)+": "+str(frequency[i])+" "+str(frequency[i]/len(texts))+"%\n")
    fwriteClass.writelines("Total block numbers: "+str(len(texts)))
    fwriteClass.close()

def openNumtopic():
    global num_topics
    fwriteclass = []
    for i in range(num_topics):
        fwriteclass.append(open("../BasicBlock/"+str(taskname)+"_writeOutput_class"+str(i)+".log", "w"))
    return fwriteclass

def closeNumtopic(fwriteNumclass):
    global num_topics
    for i in range(num_topics):
        fwriteNumclass[i].close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING) # DEBUG or WARNING
    # [binary_textes, texts,unique_block,frequencyBlock]=extractBasicblock()
    [binary_textes, texts,unique_block,frequencyBlock]=extractBasicblockFullCommand()
    logging.debug(texts)

    M = len(texts)
    print('语料库载入完成，据统计，一共有 %d 篇文档' % M)
    # [lda,corpus_tfidf,num_topics,dictionary]=LDA(texts)
    # # writeData("dictionary", dictionary)
    # # writeData("corpus_tfidf",corpus_tfidf)
    # output(lda,corpus_tfidf,num_topics,dictionary)
    # writeOutput(lda,corpus_tfidf,num_topics,dictionary,binary_textes, texts,unique_block,frequencyBlock)
