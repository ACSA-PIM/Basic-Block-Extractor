from terminal_command import TIMEOUT_COMMAND,TIMEOUT_severalCOMMAND,checkFileByRegex
from tsjPython.tsjCommonFunc import *
import global_variable as glv
from collections import defaultdict
import sys
from multiBar import time2String

def readSavePile():
    tmp_inst_text=[]
    tmp_inst_binary=[]
    tmp_inst_binary_reverse=[]

    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)

    count=0
    prefixLen=0
    matchInstructionStart=13
    matchAbbreviationStart=42
    try:
        line = sys.stdin.readline()    # 读取第一行
        while line is not None and line != '':
            if prefixLen==0:
                if re.match("^(T[a-zA-Z0-9]*) ",line):
                    prefixLen=len(re.match("^(T[a-zA-Z0-9]*) ",line).group(1))
                    ic(prefixLen)
                    matchInstructionStart=prefixLen+5
                    matchAbbreviationStart=prefixLen+34

            if count%50000==0:
                yellowPrint("scan {} lines…… write {} block to {}".format(count,len(unique_revBiblock),glv._get("pipeModeOutputPath")))
            count+=1
            ic(line)
            if line[matchInstructionStart:matchInstructionStart+4]=="0000" \
                and line[matchAbbreviationStart:matchAbbreviationStart+1]!="b" and line[matchAbbreviationStart:matchAbbreviationStart+1]!="c" \
                and line[matchAbbreviationStart:matchAbbreviationStart+3]!="nop" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="dmb" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="msr"\
                and line[matchAbbreviationStart:matchAbbreviationStart+3]!="mrs" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="svc" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="sys"\
                and line[matchAbbreviationStart:matchAbbreviationStart+3]!="isb" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="ret" and line[matchAbbreviationStart:matchAbbreviationStart+3]!="tbz"\
                and line[matchAbbreviationStart:matchAbbreviationStart+3]!="tbn": #去除b 和c开头的

                ic("read normal lines",line[matchAbbreviationStart:-1])
                tmp_inst_text.append(line[matchAbbreviationStart:-1])# 去除 \n
                tmp_inst_binary.append(line[matchAbbreviationStart-11:matchAbbreviationStart-3])
                tmp_inst_binary_reverse.append(binaryReverse(line[matchAbbreviationStart-11:matchAbbreviationStart-3]))
            elif line[matchInstructionStart:matchInstructionStart+4]=="writ" or \
                line[matchInstructionStart:matchInstructionStart+4]=="read" or \
                line[matchAbbreviationStart:matchAbbreviationStart+1]=="b":
                ic("Cut")
                if len(tmp_inst_text) > glv._get("skip_num"):
                    ic("ACC")
                    unique_revBiblock.add(str(' '.join(tmp_inst_binary_reverse)))
                    frequencyRevBiBlock[' '.join(tmp_inst_binary_reverse)] += 1
                tmp_inst_text=[]
                tmp_inst_binary=[]
                tmp_inst_binary_reverse=[]
            line = sys.stdin.readline()    # 读取下一行
    except KeyboardInterrupt:
        errorPrint("ctrl+c KeyboardInterrupt lead to Save tmp file……")
        # writePipeModeFile(unique_revBiblock,frequencyRevBiBlock)
        # passPrint("wait {} to finish at: {}".format(time2String(int(time.time()-glv._get("processBeginTime"))),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    except Exception as e:
        errorPrint("error = {}".format(e))
        writePipeModeFile(unique_revBiblock,frequencyRevBiBlock)
        raise TypeError("readSavePile Error = {}".format(e))
    writePipeModeFile(unique_revBiblock,frequencyRevBiBlock)

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
    outputTaskNameFullName=glv._get("outputTaskName")+"_useFileNum_"+str(glv._get("useFileNum"))+"_skipNum_"+str(glv._get("skip_num"))+".log"
    filename = glv._get("outputFilePath")+ outputTaskNameFullName
    fwriteblockfreq = open(filename, "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()
    yellowPrint("write {} to log Finished: {}".format(len(totalDataDict.get("unique_revBiblock")),outputTaskNameFullName))

def writePipeModeFile(unique_revBiblock,frequencyRevBiBlock):
    filename = glv._get("pipeModeOutputPath")
    fwriteblockfreq = open(filename, "w")
    for tmp_block_binary_reverse in unique_revBiblock:
        fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
    fwriteblockfreq.close()
    yellowPrint("write {} to log Finished: {}".format(len(unique_revBiblock),filename))
