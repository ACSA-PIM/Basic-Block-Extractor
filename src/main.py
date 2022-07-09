

import config  # 加载配置

import global_variable as glv
from input_process import inputParameters, isIceEnable
from terminal_command import mkdir,findTaskList,checkDiskUsage
# from DynamoRIO import DynamoRIO_Offline, findTraceList,DynamoRIO_AssemblyLog
from basicBlockGenerate import findRawLogList,write2log
from tsjPython.tsjCommonFunc import *
# from excel import *
from data import dataDictInit,mergeDataDict
from multiProcess import MultiProcessLog

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)

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
        # DynamoRIO_Offline(logEntry)
        # if not checkDiskUsage():
        #     break
        # traceList = findTraceList()
        # logEntryName =re.search( r'\/(\w*)$',logEntry).group(1)
        # for traceEntry in traceList:
        #     if re.search( '^drmemtrace\.{}\.'.format(logEntryName),traceEntry):
        #         colorPrint("trace find {}".format(traceEntry),"cyan")
        #         DynamoRIO_AssemblyLog(traceEntry)

    
    # traceList = findTraceList()
    # taskNum=0
    # for traceEntry in traceList:
    #     taskNum+=1
    #     passPrint("traceTask {:>3d}/{:>3d}: {}".format(taskNum,len(traceList),traceEntry))
    #     DynamoRIO_AssemblyLog(traceEntry)

    # isFirstSheet=1
    # taskList = glv._get("taskList")
    # for taskKey, taskName in taskList.items():
    #     # glv._set("filename",pasteFullFileName(taskKey))
    #     filename=pasteFullFileName(taskKey)
    #     ic(filename)
    #     dataDict = dataDictInit()

    #     dataDict = readPartFile(taskName,filename, dataDict)
    #     print("blockSize {} {}".format(len(dataDict.get("unique_revBiblock")),len(dataDict.get("frequencyRevBiBlock"))))
    #     [llvmerror,osacaerror] = add2Excel(wb,taskName,isFirstSheet,dataDict)
    #     excelGraphAdd(wb,taskName,llvmerror,osacaerror)
    #     isFirstSheet=0
    # excelGraphBuild(wb)
if __name__ == "__main__":
    main()