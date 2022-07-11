
import config  # 加载配置
import global_variable as glv
from input_process import inputParameters, isIceEnable,checkPipeInputMode
from terminal_command import mkdir,findTaskList,checkDiskUsage
# from DynamoRIO import DynamoRIO_Offline, findTraceList,DynamoRIO_AssemblyLog
from basicBlockGenerate import findRawLogList,write2log,readSavePile
from tsjPython.tsjCommonFunc import *
# from excel import *
from data import dataDictInit,mergeDataDict
from multiProcess import MultiProcessLog


def normalMode():
    # check directory
    mkdir(glv._get("outputFilePath"))
    
    # get exe file list
    taskList = findRawLogList()

    taskNum=0
    useFileNum=0
    totalDataDict = dataDictInit()
    for logEntry in taskList:
        taskNum+=1
        colorPrint("logEntry {:>3d}/{:>3d}: {}".format(taskNum,len(taskList),logEntry[:-1]),"magenta")
        # if logEntry[:-1]=="small.log" or logEntry[:-1]=="small2.log" or logEntry[:-1]=="middle.log":# for code test
        if glv._get("useAllFileInDirectory")=="yes" or logEntry[:-1] in glv._get("useAllFileListInDirectory") :# for code test
            useFileNum+=1
            inDict = MultiProcessLog(logEntry)
            colorPrint("Reduce part {} to tmpAll {}".format(len(inDict.get("unique_revBiblock")),len(totalDataDict.get("unique_revBiblock"))),"grey")
            totalDataDict = mergeDataDict(inDict,totalDataDict)
    glv._set("useFileNum",useFileNum)
    write2log(totalDataDict)

def main():
    ## icecream & input
    checkPipeInputMode()
    args=inputParameters()
    isIceEnable(args.debug)


    if glv._get("mode")=="normal":
        normalMode()
    elif glv._get("mode")=="pipeInputMode":
        readSavePile()
        
if __name__ == "__main__":
    main()