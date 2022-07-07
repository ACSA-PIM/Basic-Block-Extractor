import global_variable as glv
from collections import defaultdict
import time

glv._init()

glv._set("taskName", "OpenBLASRawAssembly")# alse the directory
glv._set("inputFilePath", "/home/shaojiemike/test/DynamoRIO/")
glv._set("UopsTableFilePath", "./arm2uops/UopsTable.txt")
# glv._set("findRegex", "*test*")
glv._set("outputTaskName", "openblas_utest.log")
glv._set("outputFilePath", "/home/shaojiemike/test/DynamoRIO/AssemblyBasicBlockLog/")

# glv._set("DynamoRIO-drrun","/home/shaojiemike/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun")
# glv._set("DynamoRIO-offline","/home/shaojiemike/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -m \
#             1 -t drcachesim -outdir ~/test/DynamoRIO  -offline --")
glv._set("ProcessNum",20)
# glv._set("failedRetryTimes",1)
glv._set("findTimeout",5)
glv._set("skip_num",2)
# glv._set("timeout",0) #由输入设置default值
glv._set("debug","yes")

# def pasteFullFileName(taskfilenameprefixWithoutPath):
#     taskfilenamesubfix=glv._get("taskfilenamesubfix")
#     taskfilePath=glv._get("taskfilePath")
#     taskfilenameprefix="{}/{}".format(taskfilePath,taskfilenameprefixWithoutPath)
#     return "{}.{}".format(taskfilenameprefix,taskfilenamesubfix)


