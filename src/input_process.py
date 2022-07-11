from icecream import ic
from icecream import install
import global_variable as glv
from tsjPython.tsjCommonFunc import *
import argparse
import sys

def checkPipeInputMode():
    if not sys.stdin.isatty():
        yellowPrint("using Pipe Input Mode……")
        glv._set("mode","pipeInputMode")
    else:
        yellowPrint("using normal mode……")
        glv._set("mode","normal")

def inputParameters():
    yellowPrint("In addition to entering some parameters, you can also modify all parameters in config.py")
    parser = argparse.ArgumentParser()
    parser.description = "please enter some parameters"
    # parser.add_argument(
    #     "-b",
    #     "--BHiveCount",
    #     help="BHive Count Num (maybe useless depends on bin/bhive use",
    #     dest="BHiveCount",
    #     type=int, default="500"
    # )
    if glv._get("mode")=="normal":
        parser.add_argument(
            "-p",
            "--ProcessNum",
            help="multiple Process Numbers",
            dest="ProcessNum",
            type=int, default="20"
        )
        parser.add_argument(
            "-u",
            "--useAll",
            help="is use All Files In Directory or choose a fileList in config.py",
            dest="useAllFileInDirectory",
            type=str,
            choices=["yes", "no"],
            default="no",
        )
        parser.add_argument(
            "-d",
            "--debug",
            help="is print debug informations",
            dest="debug",
            type=str,
            choices=["yes", "no"],
            default="yes",
        )
        args = parser.parse_args()
        # glv._set("BHiveCount",args.BHiveCount)
        glv._set("ProcessNum",args.ProcessNum)
        glv._set("useAllFileInDirectory",args.useAllFileInDirectory)
        glv._set("debug",args.debug)
        pPrint(glv.GLOBALS_DICT)
        # passPrint("parameter BHiveCount is : %s" % args.BHiveCount)
        passPrint("parameter ProcessNum is : %s" % args.ProcessNum)
        passPrint("parameter useAllFileInDirectory is : %s " % args.useAllFileInDirectory)
        passPrint("parameter debug is : %s " % args.debug)
    else:
        parser.add_argument(
            "-o",
            "--output",
            help="Specify the write file path in Pipe Input mode",
            dest="pipe_Mode_OutputPath",
            required=True,
            type=str
        )
        parser.add_argument(
            "-d",
            "--debug",
            help="is print debug informations",
            dest="debug",
            type=str,
            choices=["yes", "no"],
            default="yes",
        )
        args = parser.parse_args()
        glv._set("pipeModeOutputPath",args.pipe_Mode_OutputPath)
        glv._set("debug",args.debug)
        pPrint(glv.GLOBALS_DICT)
        passPrint("parameter pipeModeOutputPath is : %s " % args.pipe_Mode_OutputPath)
        passPrint("parameter debug is : %s " % args.debug)
    # yellowPrint("less timeout causes less or no output!!!")
    return args

def isIceEnable(isYes):
    install()
    ic.configureOutput(prefix='Debug -> ', outputFunction=yellowPrint)
    if isYes=="yes" : 
        ic.enable()
    else:
        ic.disable()