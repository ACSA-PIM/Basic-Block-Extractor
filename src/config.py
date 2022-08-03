import global_variable as glv
from collections import defaultdict
import time

glv._init()

# 输入
glv._set("inputFilePath", "/home/shaojiemike/test/DynamoRIO/ffmpeg")    # 输入汇编文件目录
glv._set("useAllFileInDirectory","no")                                  # 是否使用输入汇编文件目录下所有的文件，默认是不使用全部。需要指定useAllFileListInDirectory
glv._set("useAllFileListInDirectory",[
                                    "ffmpeg_Assembly.log"
                                    # "xzcblat1.log",
                                    # "middle.log",
                                    # "small2.log"
                                    ])                                  # glv._get("useAllFileInDirectory")=="no"时生效，指定目录下需要使用的汇编文件

# 结果
glv._set("outputTaskName", "ffmpeg")                                    #实际保存文件会添加后缀。outputTaskName为ffmpeg。保存文件名可能为ffmpeg_useFileNum_1_skipNum_0.log
glv._set("outputFilePath", "/home/shaojiemike/test/DynamoRIO/AssemblyBasicBlockLog/")

# 其他参数
glv._set("ProcessNum",20)                                               # 并行核数
glv._set("findTimeout",5)                                               # 子程序运行多久超时会Kill
glv._set("skip_num",0)                                                  # 输出基本块内指令数大于多少条。例如0意味着基本块内指令数至少有1条。


