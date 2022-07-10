import global_variable as glv
import multiprocessing as mp
from data import queueDictInit,dataDictInit
from multiprocessing import Pipe
from multiBar import *
from collections import defaultdict
from tsjPython.tsjCommonFunc import *
import sys
import re
# from Bhive import *
# from llvm_mca import *
# from OSACA import *
from collections import defaultdict
from basicBlockGenerate import readUopsTable,binaryReverse
import time


class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

def paralleReadProcess(filename,sendPipe,rank, startFileLine,endFileLine, queueDict):
    # unique_revBiblock_Queue,frequencyRevBiBlock_Queue,OSACAmaxCyclesRevBiBlock_Queue,OSACACPCyclesRevBiBlock_Queue,OSACALCDCyclesRevBiBlock_Queue,BhiveCyclesRevBiBlock_Queue,accuracyMax_Queue,accuracyCP_Queue,llvmmcaCyclesRevBiBlock_Queue,accuracyLLVM_Queue):
    ic("MPI Process Start {:2d} {}~{}".format(rank,startFileLine,endFileLine))
    fread=open(filename, 'r')

    # subDataDict=dataDictInit()
    # textNum=0
    tmp_inst_text=[]
    # tmp_full_inst_text=[]
    tmp_inst_binary=[]
    tmp_inst_binary_reverse=[]
    unique_revBiblock=set()
    frequencyRevBiBlock = defaultdict(int)

    matchers = readUopsTable()
    sendSkipNum=int((endFileLine-startFileLine)/400)+1
    # for line in tqdm(fread.readlines()[startFileLine:endFileLine],total=endFileLine-startFileLine,desc=str("{:2d}".format(rank))):
    totalLine=0
    partLine=1
    prefixLen=0
    matchInstructionStart=13
    matchAbbreviationStart=42
    try:
        # for line in fread.readline():
        line = fread.readline()    # 读取第一行
        while line is not None and line != '':
            if prefixLen==0:
                prefixLen=len(re.match("^(T[a-zA-Z0-9]*) ",line).group(1))
                ic(prefixLen)
                matchInstructionStart=prefixLen+5
                matchAbbreviationStart=prefixLen+34
            if totalLine<startFileLine:
                totalLine+=1
                continue
            elif totalLine>=endFileLine:
                break
            totalLine+=1

            if partLine%sendSkipNum==0:
                sendPipe.send(partLine)
            partLine+=1
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
            line = fread.readline()    # 读取下一行
    except Exception as e:
        sendPipe.send(e)
        errorPrint("error = {}".format(e))
        raise TypeError("paralleReadProcess = {}".format(e))
    fread.close() 
    ic("---------------------SubProcess logEntry-------------------------")
    ic(unique_revBiblock)
    ic(frequencyRevBiBlock)
    queueDict.get("frequencyRevBiBlock").put(frequencyRevBiBlock)
    queueDict.get("unique_revBiblock").put(unique_revBiblock)
    sendPipe.send(partLine+sendSkipNum)
    sendPipe.close()
    ic("MPI Process end {:2d} {}~{}".format(rank,startFileLine,endFileLine))

def fileLineNum(filename):
    # filename=glv._get("filename")
    yellowPrint("Reading file Lines Num...")
    fread=open(filename, 'r')
    num_file = sum([1 for i in open(filename, "r")])
    glv._set("num_file",num_file)
    fread.close() 
    return num_file

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
        passPrint("wait {} to finish reading file Lines Num {} at: {}".format(time2String(int(time.time()-processBeginTime)),totalNum,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        return totalNum

def mergeQueue2dataDict(queueDict,dataDict):
    for key, value in dataDict.dataDict.items():
        # ic(key,type(value))
        if isinstance(value,set):
            # ic("set")
            dataDict.dataDict[key]=dataDict.dataDict[key].union(queueDict.dataDict[key].get())
        elif isinstance(value,defaultdict):
            # ic("defaultdict(int)")
            dataDict.dataDict[key].update(queueDict.dataDict[key].get())
    return dataDict
def reduceQueue2dataDict(queueDict,dataDict):
    for key, value in dataDict.dataDict.items():
        # ic(key,type(value))
        if isinstance(value,set):
            # ic("set")
            dataDict.dataDict[key]=dataDict.dataDict[key].union(queueDict.dataDict[key].get())
        elif isinstance(value,defaultdict):
            # ic("defaultdict(int)")
            a=dataDict.dataDict[key]
            b=queueDict.dataDict[key].get()
            for key2 in b:
                dataDict.dataDict[key][key2]=a[key2]+b[key2]
    return dataDict

def MultiProcessLog(logEntry):
    filename=glv._get("inputFilePath")+glv._get("taskName")+"/"+logEntry[:-1]
    ic(filename)
    num_file=fastfileLineNum(filename)
    ic("logfileline is {}".format(num_file))
    ProcessNum=glv._get("ProcessNum")

    dataDict = dataDictInit()
    queueDict = queueDictInit(dataDict)

    sendPipe=dict()
    receivePipe=dict()
    total=dict()

    pList=[]
    for i in range(ProcessNum):
        startFileLine=int(i*num_file/ProcessNum)
        endFileLine=int((i+1)*num_file/ProcessNum)
        receivePipe[i], sendPipe[i] = Pipe(False)
        total[i]=endFileLine-startFileLine
        pList.append(Process(target=paralleReadProcess, args=(filename,sendPipe[i],i,startFileLine,endFileLine,queueDict)))

    for p in pList:
        p.start()
    
    taskName=glv._get("taskName")+" "+logEntry[:-1]
    # https://stackoverflow.com/questions/19924104/python-multiprocessing-handling-child-errors-in-parent
    if glv._get("debug")=='no':
        stdscr = curses.initscr()
        multBar(taskName,ProcessNum,total,sendPipe,receivePipe,pList,stdscr)
    
    ic(queueDict.get("unique_revBiblock").qsize())
    while queueDict.get("unique_revBiblock").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("unique_revBiblock").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    # for p in pList:
    #     p.join() # 避免僵尸进程
        
    # for i in tqdm(range(ProcessNum)):
    for i in range(ProcessNum):
        dataDict=reduceQueue2dataDict(queueDict,dataDict)
    ic("---------------------logEntry-------------------------")
    ic(dataDict.get("unique_revBiblock"))
    ic(dataDict.dataDict["frequencyRevBiBlock"])
    return dataDict

def readPartFile(taskName,filename, dataDict):
    # unique_revBiblock,frequencyRevBiBlock,OSACAmaxCyclesRevBiBlock,OSACACPCyclesRevBiBlock,OSACALCDCyclesRevBiBlock,BhiveCyclesRevBiBlock,accuracyMax,accuracyCP,llvmmcaCyclesRevBiBlock,accuracyLLVM):
    num_file=fileLineNum(filename)
    ProcessNum=glv._get("ProcessNum")

    queueDict = queueDictInit(dataDict)

    sendPipe=dict()
    receivePipe=dict()
    total=dict()

    pList=[]
    for i in range(ProcessNum):
        startFileLine=int(i*num_file/ProcessNum)
        endFileLine=int((i+1)*num_file/ProcessNum)
        receivePipe[i], sendPipe[i] = Pipe(False)
        total[i]=endFileLine-startFileLine
        pList.append(Process(target=paralleReadProcess, args=(filename,sendPipe[i],i,startFileLine,endFileLine,queueDict)))

    for p in pList:
        p.start()
    

    # https://stackoverflow.com/questions/19924104/python-multiprocessing-handling-child-errors-in-parent
    if glv._get("debug")=='no':
        stdscr = curses.initscr()
        multBar(taskName,ProcessNum,total,sendPipe,receivePipe,pList,stdscr)
    
    while queueDict.get("unique_revBiblock").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("unique_revBiblock").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    # for p in pList:
    #     p.join() # 避免僵尸进程
        
    # for i in tqdm(range(ProcessNum)):
    for i in range(ProcessNum):
        # print("MPISum rank : {}, blockNum : {},leftQueueNum : {}".format(i,len(unique_revBiblock),unique_revBiblock_Queue.qsize()))
        dataDict=mergeQueue2dataDict(queueDict,dataDict)
    return dataDict
    # print(unique_revBiblock)
    # print(frequencyRevBiBlock)
    # print(accuracyMax)
    # print(len(unique_revBiblock))
    # print(len(frequencyRevBiBlock))