from mergeConfig import *
from collections import defaultdict
from tsjPython.tsjCommonFunc import *
from tqdm import tqdm 

unique_revBiblock=set()
frequencyRevBiBlock=defaultdict(int)


def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b

def fastfileLineNum(filename):
    yellowPrint("fast reading file Lines Num...at: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    processBeginTime=time.time()
    with open(filename, "r",encoding="utf-8",errors='ignore') as f:
        totalNum = sum(bl.count("\n") for bl in blocks(f))
        passPrint("finish reading file Lines Num {} at: {}".format(totalNum,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        return totalNum

def readEntry2Merge(mergeEntry,unique_revBiblock,frequencyRevBiBlock):
    mergeEntrylinesNum = fastfileLineNum(mergeEntry)
    fread=open(mergeEntry, 'r')
    line = fread.readline()    # 读取第一行
    pbar = tqdm(total=mergeEntrylinesNum)
    while line is not None and line != '':
        block=re.search('^(.*),',line).group(1)
        num=re.search(',(.*)$',line).group(1)
        unique_revBiblock.add(block)
        frequencyRevBiBlock[block]+=int(num)
        pbar.update(1)
        line = fread.readline()    # 读取第一行

def saveMergeResult(saveFilePath,unique_revBiblock,frequencyRevBiBlock):
    fileWriteBlockFreq = open(saveFilePath, "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fileWriteBlockFreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fileWriteBlockFreq.close()
    yellowPrint("write {} to log Finished: {}".format(len(unique_revBiblock),saveFilePath))

def main():
    taskNum=0
    for mergeEntry in mergeList:
        taskNum+=1
        colorPrint("mergeEntry {:>3d}/{:>3d}: {}".format(taskNum,len(mergeList),mergeEntry),"magenta")
        beforeMergeNum=len(unique_revBiblock)
        readEntry2Merge(mergeEntry,unique_revBiblock,frequencyRevBiBlock)
        colorPrint("merge num from {} Up to {}".format(beforeMergeNum,len(unique_revBiblock)),"grey")
    saveMergeResult(saveFilePath,unique_revBiblock,frequencyRevBiBlock)

if __name__ == "__main__":
    main()