from terminal_command import TIMEOUT_COMMAND,TIMEOUT_severalCOMMAND,checkFileByRegex
from tsjPython.tsjCommonFunc import *
import global_variable as glv

def findRawLogList():
    command='ls '+glv._get("inputFilePath")+glv._get("taskName")
    RawLogList=TIMEOUT_severalCOMMAND(command,glv._get("findTimeout"))
    ic(RawLogList)
    return RawLogList

def readUopsTable():
    data = {}
    with open(glv._get("UopsTableFilePath"), 'r') as f:#with语句自动调用close()方法
        line = f.readline()
        while line:
            # data[line[0:6]]=line[8:-1]
            data[line[8:-1]]=line[0:6]
            line = f.readline()
    return data #返回数据为双列表形式

def binaryReverse(string):
    return string[6:8]+string[4:6]+string[2:4]+string[0:2]

def write2log(totalDataDict):
    ic(totalDataDict.get("unique_revBiblock"))
    ic(totalDataDict.dataDict["frequencyRevBiBlock"])
    unique_revBiblock = totalDataDict.get("unique_revBiblock")
    frequencyRevBiBlock = totalDataDict.dataDict["frequencyRevBiBlock"]
    filename = glv._get("outputFilePath")+ glv._get("outputTaskName")
    fwriteblockfreq = open(filename, "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()
    yellowPrint("write {} to log Finished: {}".format(len(totalDataDict.get("unique_revBiblock")),glv._get("outputTaskName")))