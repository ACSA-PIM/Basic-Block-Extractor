# BHive-Extract-A64-Blocks-kunpeng

通过使用DynamoRIO在ARM64上采集运行程序的汇编。经过筛选，去重汇总统计，最后得到精简的基本块信息。
## 仓库功能

![](https://shaojiemike.oss-cn-hangzhou.aliyuncs.com/img/20220712145409.png)

本仓库代码实现了对DynamoRIO产生的汇编筛选，去重汇总统计，最后得到精简的基本块信息。对应图中红框蓝底部分。


## 安装

### DynamoRIO安装

在[https://dynamorio.org/page_releases.html](https://dynamorio.org/page_releases.html) 下载对应版本[DynamoRIO-AArch64-Linux-9.0.1.tar.gz](https://github.com/DynamoRIO/dynamorio/releases/download/release_9.0.1/DynamoRIO-AArch64-Linux-9.0.1.tar.gz), 

解压即可运行。`./DynamoRIO-AArch64-Linux-9.0.1/bin64/drrun` 为之后所需的程序

```bash
tar -xvf DynamoRIO-AArch64-Linux-9.0.1.tar.gz
```

### 仓库代码依赖安装
```
pip install -r requirements.txt
```
## 运行DynamoRIO采集汇编
由于采集机器的底层运行二进制指令(汇编)是繁琐的。DynamoRIO采集分析汇编所需时间是以天为单位的，汇编的空间占用也是TB级别的。(具体空间时间需求可以看前图)

DynamoRIO采集汇编分成两步：
### 1 offline模式采集Raw数据
```
~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -jobs 10 -outdir /addDisk/DiskNo3 -offline -- ./exe
```
运行该命令，会并行10核会在路径`/addDisk/DiskNo3` 下生成`drmemtrace.exe.24491.9635.dir`目录，保留Raw文件。时间是单独执行程序的2~3倍。

### 2 解析Raw产生汇编
```
~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -simulator_type view -indir /addDisk/DiskNo3/drmemtrace.exe.24491.9635.dir 2>&1 > result.log
```
运行该命令，会解析`/addDisk/DiskNo3/drmemtrace.exe.24491.9635.dir`目录下的Raw文件，并从终端输出(或者重定向到`result.log`文件)。

根据原始`drmemtrace.exe.24491.9635.dir`目录大小，耗时10~40h不等。(原始50GB文件夹解析后，文件夹增大到250G左右，可以产生800GB的原始汇编，总耗时35h)

## 运行仓库代码处理汇编
DynamoRIO原始汇编保留下来是TB量级，处理之后结果文件不超过10MB。
### Run Way1 : 实时处理DynamoRIO输出的汇编
**推荐以这种方式运行，不需要保留汇编文件**

例子(注意该情况是串行，将DynamoRIO的第二条指令的输出重定向给程序)：
```
~/Download/DynamoRIO-AArch64-Linux-8.0.18895/bin64/drrun -t drcachesim -simulator_type view -indir drmemtrace.fftw_dft_r2c_1d_c_example.exe.987366.7729.dir 2>&1|python ./src/main.py -o ~/fftw.log -d no
```
或者
```
cat small_assembly.log |python ./src/main.py -o ~/test.result -d no
```
| 参数		|说明	|
|---		|---	|
|-o	    |输出文件路径
|-d     |是否打印debug信息(默认no)

### Run Way2 : 并行处理已有汇编文件

如果已有汇编文件，可以并行加速处理。

需要修改`./src/config.py`里的配置，解释如下：



| 参数		|说明	|
|---		|---	|
|inputFilePath	            |输入汇编文件目录
|useAllFileInDirectory      |是否使用输入汇编文件目录下所有的文件，默认是不使用全部。需要指定useAllFileListInDirectory(考虑到将文件夹下多个汇编文件汇总统计的需求)
|useAllFileListInDirectory  |glv._get("useAllFileInDirectory")=="no"时生效，指定目录下需要使用的汇编文件
|outputTaskName             |输出文件名。实际保存文件会添加后缀。假设outputTaskName为ffmpeg。保存文件名可能为ffmpeg_useFileNum_1_skipNum_0.log
|outputFilePath             |输出文件目录
|ProcessNum                 |并行核数
|findTimeout                |子程序运行多久超时会Kill
|skip_num                   | 输出基本块内指令数大于多少条。例如0意味着基本块内指令数至少有1条。

例子：
```
python ./src/main.py -p 25 -d no
```

25核并行处理300G log 需要30分钟左右。

