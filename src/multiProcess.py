import global_variable as glv
import multiprocessing as mp
from data import queueDictInit,dataDictInit
from multiprocessing import Pipe
from multiBar import *
from collections import defaultdict
from tsjPython.tsjCommonFunc import *
import sys
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
    # for line in tqdm(fread.readlines()[startFileLine:endFileLine],total=endFileLine-startFileLine,desc=str("{:2d}".format(rank))):
    totalLine=0
    partLine=1
    try:
        # for line in fread.readline():
        line = fread.readline()    # 读取第一行
        while line is not None and line != '':
            if totalLine<startFileLine:
                totalLine+=1
                continue
            elif totalLine>=endFileLine:
                break
            totalLine+=1

            if partLine%20==0:
                sendPipe.send(partLine)
            partLine+=1
            ic(line)
            if line[13:17]=="0000" and line[42:43]!="b" and line[42:43]!="c" \
                and line[42:45]!="nop" and line[42:45]!="dmb" and line[42:45]!="msr"\
                and line[42:45]!="mrs" and line[42:45]!="svc" and line[42:45]!="sys"\
                and line[42:45]!="isb" and line[42:45]!="ret" and line[42:45]!="tbz"\
                and line[42:45]!="tbn": #去除b 和c开头的
                # tmp_inst_text.append(line[42:-1])
                # ic("read normal lines",line[42:-1])
                tmp_inst_text.append(line[42:-1])# 去除 \n
                    # tmp_full_inst_text.append(line[42:])
                tmp_inst_binary.append(line[31:39])
                tmp_inst_binary_reverse.append(binaryReverse(line[31:39]))
            elif line[13:17]=="writ" or line[13:17]=="read" or line[42:43]=="b":
                # ic("Cut")
                if len(tmp_inst_text) > glv._get("skip_num"):
                    # ic("ACC")
                    # ic(tmp_inst_binary_reverse)
                    # textNum+=1
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
    queueDict.get("unique_revBiblock").put(unique_revBiblock)
    queueDict.get("frequencyRevBiBlock").put(frequencyRevBiBlock)
    sendPipe.send(50000)
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
    
    taskName=glv._get("taskName")+logEntry[:-1]
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