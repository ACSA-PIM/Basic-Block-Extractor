from tsjPython.tsjCommonFunc import *
from tqdm import *
from collections import defaultdict


def binaryReverse(string):
    return string[6:8]+string[4:6]+string[2:4]+string[0:2]

skip_num=2
rank=0
taskname='test_insns'
datafile='./'+taskname+'.txt'
ignoreList=["nop","dmb" ,"msr","mrs","svc","sys","isb" ,"ret" ,"tbz","tbn"]
textNum=0
tmp_inst_text=[]
# tmp_full_inst_text=[]
tmp_inst_binary=[]
tmp_inst_binary_reverse=[]
unique_revBiblock=set()
frequencyRevBiBlock = defaultdict(int)

fread = open(datafile, "r")
val = os.popen("wc -l {}".format(datafile))
list = val.readlines()
regexResult=re.search("^([0-9]*) ",list[0])
num_file=int(regexResult.group(1))
print("文件名: {} {}".format(fread.name,num_file))

for line in tqdm(fread,total=num_file,desc=str("{:2d}".format(rank))):
	result= re.findall(r'0xfffe\w{8} 0x(\w{8}) (.*)$', line)
	if result:
		passPrint("find some {}".format(result))
		print(result[0][1][0:3])
		if result[0][1][0]!='b' and result[0][1][0]!='c' and result[0][1][0:3] not in ignoreList:
			yellowPrint(result[0][1][0:3])
			tmp_inst_text.append(result[0][1])# 去除 \n
			tmp_inst_binary.append(result[0][0])
			tmp_inst_binary_reverse.append(binaryReverse(result[0][0]))
		elif result[0][1][0]=='b':
			errorPrint("break {}".format(len(tmp_inst_text)))
			if len(tmp_inst_text) > skip_num:
				textNum+=1
				unique_revBiblock.add(str(' '.join(tmp_inst_binary_reverse)))
				frequencyRevBiBlock[' '.join(tmp_inst_binary_reverse)] += 1
			tmp_inst_text=[]
			tmp_inst_binary=[]
			tmp_inst_binary_reverse=[]
	else:
		errorPrint("ops!")
fread.close()
fwriteblockfreq = open('./'+taskname+'_blockFrequency_skip_'+str(skip_num)+".log", "w")
for tmp_block_binary_reverse in unique_revBiblock:
	fwriteblockfreq.writelines(tmp_block_binary_reverse+','+str(frequencyRevBiBlock[tmp_block_binary_reverse])+"\n")
fwriteblockfreq.close()

import shutil

original = r'./'+taskname+'_blockFrequency_skip_'+str(skip_num)+".log"
target = r'/home/shaojiemike/blockFrequency/'+taskname+'_blockFrequency_skip_'+str(skip_num)+".log"

shutil.copyfile(original, target)