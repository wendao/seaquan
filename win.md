# 在Windows下安装WSL及相关R包

## WSL的安装

```
Windows Subsystem for Linux（简称WSL）是一个为在Windows 10上
能够原生运行Linux二进制可执行文件（ELF格式）的兼容层。它是由微软
与Canonical公司合作开发，目标是使纯正的Linux能下载和解压到用户的
本地计算机，并且映像内的工具和实用工具能在此子系统上原生运行。
—— 百度百科
```

1. 在**控制面板-程序与功能**中启用 **适用于Linux的Windows子系统**

<img src="docs/wsl-1.jpg" alt="img" style="zoom:67%;" />

2. 在**Windows应用商店**搜索**ubuntu**，并安装，这里推荐**18.04**，可以方便的读取windows系统的其它文件

3. 安装完成后，从开始菜单或应用商店启动ubuntu，创建用户和密码

4. 国内可以考虑更换apt的源，如阿里源

```
#sudo vi /etc/apt/sources.list
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
```

5. 安装必要包

```
sudo apt install libxml2-dev libnetcdf-dev zlib1g-dev libc6-dev-i386
```


## conda环境的安装

conda是一个可以方便的管理各种python以及生信包的工具，避免大量手动操作

1. 从[conda官网](https://docs.conda.io/en/latest/miniconda.html)下载ubuntu安装包，并默认安装

2. 建立工作环境，可以参考这个[链接](https://pythonforundergradengineers.com/new-virtual-environment-with-conda.html)

```
conda create -n ms python=3.6
conda activate ms
```

3. 安装[bioconductor](https://www.bioconductor.org/)下的R环境
```
conda install -c bioconda r-base=3.6.1
```

4. 在R中测试是否安装成功，在命令行中运行R

## XCMS的安装

1. 在R中运行,不同版本可以通过注释行切换（如R 3.6.1 对应 bioconductor 3.10）
```
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
#BiocManager::install(version = "3.10")
```

2. 自动安装XCMS
```
BiocManager::install("xcms", INSTALL_opts = '--no-lock')
```

3. 可能遇到的问题及其解法
```
#无法安装MALDIquant，先去下载适合R版本的源代码（本例中1.18测试通过）
https://cran.r-project.org/src/contrib/Archive/MALDIquant/
install.packages("MALDIquant-1.18.tar.gz", repos = NULL, type="source")
```


## CIMAGE的安装

直接从[GITHUB](https://github.com/wangchulab/CIMAGE2)克隆或下载即可，需要在环境变量中指定路径

```
export CIMAGE_PATH=your_folder
```

具体操作见手册

