import global_variable as glv
from collections import defaultdict
import time

glv._init()

glv._set("taskName", "OpenBLASRawAssembly")# alse the directory
glv._set("inputFilePath", "/home/shaojiemike/test/DynamoRIO/") #DynamoRIO/
glv._set("UopsTableFilePath", "./arm2uops/UopsTable.txt")

glv._set("outputTaskName", "OpenBLAS_test3")
glv._set("outputFilePath", "/home/shaojiemike/test/DynamoRIO/AssemblyBasicBlockLog/")

glv._set("useAllFileInDirectory","no")
glv._set("useAllFileListInDirectory",[
                                    "xscblat2.log"
                                    # "xzcblat1.log",
                                    # "middle.log",
                                    # "small2.log"
                                    ])


glv._set("ProcessNum",20)
# glv._set("failedRetryTimes",1)
glv._set("findTimeout",5)
glv._set("skip_num",0)
# glv._set("timeout",0) #由输入设置default值
glv._set("debug","yes")
glv._set("sendSkipNum",2000)

# def pasteFullFileName(taskfilenameprefixWithoutPath):
#     taskfilenamesubfix=glv._get("taskfilenamesubfix")
#     taskfilePath=glv._get("taskfilePath")
#     taskfilenameprefix="{}/{}".format(taskfilePath,taskfilenameprefixWithoutPath)
#     return "{}.{}".format(taskfilenameprefix,taskfilenamesubfix)


