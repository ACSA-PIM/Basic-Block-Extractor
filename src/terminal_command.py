import os
from tsjPython.tsjCommonFunc import *
import global_variable as glv

def findTaskList():
    command="find "+glv._get("inputFilePath")+" -path "+glv._get("findRegex")+" -executable -type f"
    inputTaskList=TIMEOUT_COMMAND(command,glv._get("findTimeout"))
    ic(inputTaskList)
    return inputTaskList

def checkFileByRegex(nameRegex, checkPath):
    # command="find "+glv._get("inputFilePath")+" -path \""+glv._get("findRegex")+"\"|wc -l"
    # findNum=TIMEOUT_COMMAND(command,glv._get("findTimeout"))
    # ic(findNum)
    lsList=os.listdir(checkPath)
    ic(lsList)
    for lsEntry in lsList:
        ic(lsEntry)
        if re.search(nameRegex,lsEntry):
            colorPrint("%s existed"% nameRegex,"blue")
            return True
    errorPrint("%s NOT existed"% nameRegex)
    return False

def checkDiskUsage():
    command="df -h ."
    yellowPrint(command)
    duText=TIMEOUT_severalCOMMAND(command,glv._get("findTimeout"))
    ic(duText)
    UsagePercent = re.search("([0-9]*)\%",duText[1]).group(1)
    ic(UsagePercent)
    if int(UsagePercent)>90:
        errorPrint("Disk is near fulled %s%" % UsagePercent)
        return False
    else:
        colorPrint("DiskUsage is OK {}%".format(UsagePercent), "magenta")
        return True

# def checkFile(taskfilePath):
#     tmpOSACAfilePath=taskfilePath+"/tmpOSACAfiles"
#     mkdir(tmpOSACAfilePath)
#     return tmpOSACAfilePath

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
		ic("---  new folder... %s ---"%(path))
	else:
		ic("---  There is this folder! %s  ---"%(path))

def TIMEOUT_COMMAND(command, timeout=10):
    ic(command)
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    cmd = command.split(" ")
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding="utf-8",preexec_fn=os.setsid) #让 Popen 成立自己的进程组
    # https://www.cnblogs.com/gracefulb/p/6893166.html
    # 因此利用这个特性，就可以通过 preexec_fn 参数让 Popen 成立自己的进程组， 然后再向进程组发送 SIGTERM 或 SIGKILL，中止 subprocess.Popen 所启动进程的子子孙孙。当然，前提是这些子子孙孙中没有进程再调用 setsid 分裂自立门户。
    ic("TIMEOUT_COMMAND-before",process.pid,process.poll())
    # while process.poll() != 208 and  process.poll() != 0: # poll()(好像BHive208是正常结束)返回0 正常结束， 1 sleep， 2 子进程不存在，-15 kill，None 在运行
    while process.poll()==None or process.poll()==1:
        time.sleep(2)
        now = datetime.datetime.now()
        ic("TIMEOUT_COMMAND-During",process.pid,process.poll(),(now - start).seconds)
        if (now - start).seconds> timeout:
            # BHive有子进程，需要杀死进程组。但是需要新生成进程组，不然会把自己kill掉
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            # os.killpg(process.pid, signal.SIGTERM) SIGTERM不一定会kill，可能会被忽略，要看代码实现
            # https://blog.csdn.net/zhupenghui176/article/details/109097737
            # os.waitpid(-1, os.WNOHANG)
            (killPid,killSig) = os.waitpid(process.pid, 0)
            if killPid != process.pid or killSig!=9:
                errorPrint("TIMEOUT_COMMAND kill failed! killPid %d process.pid %d killSig %d" % (killPid, process.pid, killSig))
            ic("Killed",process.pid,process.poll())
            return None
    ic("TIMEOUT_COMMAND-Finished",process.pid,process.poll())
    return process.stdout.readlines()


def TIMEOUT_severalCOMMAND(command, timeout=10):
    ic(command)
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    start = datetime.datetime.now()
    process = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding="utf-8",preexec_fn=os.setsid) #让 Popen 成立自己的进程组
    # https://www.cnblogs.com/gracefulb/p/6893166.html
    # 因此利用这个特性，就可以通过 preexec_fn 参数让 Popen 成立自己的进程组， 然后再向进程组发送 SIGTERM 或 SIGKILL，中止 subprocess.Popen 所启动进程的子子孙孙。当然，前提是这些子子孙孙中没有进程再调用 setsid 分裂自立门户。
    ic("TIMEOUT_COMMAND-before",process.pid,process.poll())
    # while process.poll() != 208 and  process.poll() != 0: # poll()(好像BHive208是正常结束)返回0 正常结束， 1 sleep， 2 子进程不存在，-15 kill，None 在运行
    while process.poll()==None or process.poll()==1:
        time.sleep(2)
        now = datetime.datetime.now()
        ic("TIMEOUT_COMMAND-During",process.pid,process.poll(),(now - start).seconds)
        if (now - start).seconds > timeout:
            # BHive有子进程，需要杀死进程组。但是需要新生成进程组，不然会把自己kill掉
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            # os.killpg(process.pid, signal.SIGTERM) SIGTERM不一定会kill，可能会被忽略，要看代码实现
            # https://blog.csdn.net/zhupenghui176/article/details/109097737
            # os.waitpid(-1, os.WNOHANG)
            (killPid,killSig) = os.waitpid(process.pid, 0)
            if killPid != process.pid or killSig!=9:
                errorPrint("TIMEOUT_COMMAND kill failed! killPid %d process.pid %d killSig %d" % (killPid, process.pid, killSig))
            ic("Killed",process.pid,process.poll())
            return None
    ic("TIMEOUT_COMMAND-Finished",process.pid,process.poll())
    return process.stdout.readlines()

# def TIMEOUT_severalCOMMAND(command, timeout=10):
#     """call shell-command and either return its output or kill it
#     if it doesn't normally exit within timeout seconds and return None"""
#     import subprocess, datetime, os, time, signal
#     start = datetime.datetime.now()
#     process = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding="utf-8")
#     ic("LLVM-before",process.pid,process.poll())
#     while process.poll() is None: # poll()返回0 正常结束， 1 sleep， 2 子进程不存在，-15 kill，None 在运行
#         ic("LLVM-During",process.pid,process.poll())
#         time.sleep(0.2)
#         now = datetime.datetime.now()
#         if (now - start).seconds> timeout:
#             os.kill(process.pid, signal.SIGKILL)
#             # https://blog.csdn.net/zhupenghui176/article/details/109097737
#             # os.waitpid(-1, os.WNOHANG)
#             (killPid,killSig) = os.waitpid(process.pid, 0)
#             if killPid != process.pid or killSig!=9:
#                 errorPrint("TIMEOUT_COMMAND kill failed! killPid %d process.pid %d killSig %d" % (killPid, process.pid, killSig))
#             ic("LLVM-Killed",process.pid,process.poll())
#             return None
#     ic("LLVM-Finished",process.pid,process.poll())
#     return process.stdout.readlines()   

