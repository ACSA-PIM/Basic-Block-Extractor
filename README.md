# BHive-Extract-A64-Blocks-kunpeng

## 仓库功能

![](https://shaojiemike.oss-cn-hangzhou.aliyuncs.com/img/20220712145409.png)


## 安装
```
pip install -r requirements.txt
```

## 运行
### 设置config

请根据注释含义修改`./src/config.py`的参数。

### Run Case1 : 管道输入数据运行
例子(注意该情况是串行)：
```
~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -simulator_type view -indir drmemtrace.fftw_dft_r2c_1d_c_example.exe.987366.7729.dir 2>&1|python ~/github/BHive-Extract/src/main.py -o ~/fftw.log -d no
```
或者
```
cat small_assembly.log |python ./src/main.py -o ~/test.result -d no
```

### Run Case2 : 并行处理
注意该情况一定要修改`./src/config.py`里的输入汇编文件目录`inputFilePath`

并行处理config下对应文件，例子：
```
python ./src/main.py -p 25 -d no
```
## 其他说明
### 程序流程简介

1. 对于指定目录，某个应用的所有例子的汇编文件
2. 依次对其中的每一个进行处理
    1. 多进程读取各自的部分，处理
    2. Reduce
3. 暂时存储部分结构，重复2。 最后统一写入
    1. (由于去除，精简，和只需要二进制汇编)结果文件不超过10MB
### 串行并行时间估计以及加速比

并行处理: 300G log 读取行数是 10分钟。25核并行，处理1/25部分的时间是10分钟。最后一个进程要读大约10分钟才开始。总计30分钟左右。

串行：10*25 分钟。

加速比大约 25/3=8倍。

## To do

### pipe Input mode 

但是这样跑轻松上2万。按照原本方法只有2000？ 是pipe缓存区溢出吗？导致block打乱？

而且运行时发现数据具有严重的长尾效应。
