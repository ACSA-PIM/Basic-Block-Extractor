'''
Descripttion:
version:
Author: Shaojie Tan
Date: 2021-12-03 10:20:28
LastEditors: Shaojie Tan
LastEditTime: 2021-12-11 09:49:46
'''
from collections import defaultdict
import re

def readPartFile(i,unique_revBiblock,frequencyRevBiBlock):
    filename="{}/{}{:02d}{}".format(partFolder,taskfilenameprefix,i,taskfilenamesubfix)
    print(filename)
    with open(filename, 'r') as f:#with语句自动调用close()方法
        line = f.readline()
        while line:
            # print(re.search('^(.*),',line).group(1))
            # print(re.search(',(.*)$',line).group(1))
            block=re.search('^(.*),',line).group(1)
            num=re.search(',(.*)$',line).group(1)
            unique_revBiblock.add(block)
            frequencyRevBiBlock[block] += int(num)
            line = f.readline()
    # return data #返回数据为双列表形式

def saveAllResult(unique_revBiblock,frequencyRevBiBlock):
    filename="{}/{}all{}".format(partFolder,taskfilenameprefix,taskfilenamesubfix)
    fwriteblockfreq = open(filename, "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()

if __name__ == "__main__":
    global partFolder,taskfilenameprefix,taskfilenamesubfix,partNum
    partFolder="../blockFrequency"
    taskfilenameprefix="Gzip_"
    taskfilenamesubfix="_skip_2.log"
    partNum=17
    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)

    for i in range(partNum): #[0,partNum-1]
        print("i {}".format(i))
        readPartFile(i,unique_revBiblock,frequencyRevBiBlock)
        print("blockSize {} {}".format(len(unique_revBiblock),len(frequencyRevBiBlock)))

    saveAllResult(unique_revBiblock,frequencyRevBiBlock)
