# BHive-Extract-A64-Blocks-kunpeng

## 程序流程

1. 对于指定目录，为某个应用的所有例子的Raw汇编log
2. 对其中的每一个进行处理
    1. 多进程读取各自的部分，处理
    2. Reduce
3. 暂时存储，重复2。 最后统一写入
    1. (由于去除，精简，和只需要二进制汇编)结果文件不超过10MB

## 并行时间估计

300G log 读取行数是 10分钟

并行25，处理1/25部分的时间是10分钟

最后一个进程要读大约10分钟才开始。总计30分钟左右

## 假如串行

10*25 分钟。加速比 25/3=8倍。

## Doing

### add command pipe Input Support

```
~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -simulator_type view -indir drmemtrace.fftw_dft_r2c_1d_c_example.exe.987366.7729.dir 2>&1|python ~/github/BHive-Extract/src/main.py -o ~/fftw.log -d no

time ~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -simulator_type view -indir drmemtrace.python3.8.4097740.2425.dir | python ./src/main.py -outFile ~/test.result

cat small_assembly.log |python ./src/main.py -outFile ~/test.result
```

但是这样跑轻松上2万。按照原本方法只有2000？ 是pipe缓存区溢出吗？导致block打乱？

而且数据具有严重的长尾效应。
