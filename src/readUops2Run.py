'''
Descripttion: 
version: 
Author: Shaojie Tan
Date: 2021-11-16 09:08:58
LastEditors: Shaojie Tan
LastEditTime: 2021-11-16 09:55:15
'''

# https://stackoverflow.com/questions/27745500/how-to-save-a-list-to-a-file-and-read-it-as-a-list-type
import pickle

# taskname="Eigen_MM"
# datafile="../../../test/Eigen_MM.log"
# taskname="test"
# datafile="../test/test.log"
taskname="Eigen_10W"
datafile="../../../test/Eigen_MM_10W.log"
# taskname="Eigen_100W"
# datafile="../../../test/Eigen_MM_100W.log"
# taskname="Eigen_1000W"
# datafile="../../../test/Eigen_MM_1000W.log"
num_topics = 2
skip_num=2
saveFolder="uops"

if __name__ == "__main__":
    # binary_textes=[]
    with open("../"+saveFolder+"/Full_"+str(taskname)+"_skip_"+str(skip_num)+"_uops.log", 'rb') as f:#with语句自动调用close()方法
        binary_textes = pickle.load(f)
    print(binary_textes)