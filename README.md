# 动态路由后端

## 项目描述

根据主机telnet连接网络设备的技术以及Python等技术，实现基于Web的网络拓扑搭建及校验的自动化。

> telnet连接网络设备的技术参考附件文件
>
> telnet访问交换机：https://wenku.baidu.com/view/b2410527a31614791711cc7931b765ce05087ae5.html

本项目实现了一个拓扑，包括一台交换机以及三台路由器，主题为动态路由。

项目后端基于Flask搭建，Flask是一个使用Python编写的轻量级Web应用程序框架。

## 网络拓补

![Topography.png](https://i.loli.net/2021/01/08/lgf3pVIZxwBGokW.png)

## 运行环境

Python 3.8.7 with Flask 1.1.2, flask_cors 3.0.9, IPy 1.1

## 构建安装

需要完成物理拓扑搭建，其余所有操作在浏览器客户端完成

程序入口: app.py

```
# Switch2
Vlan1               172.16.0.1/16

# Router0
FastEthernet0/0     172.16.0.2/16
FastEthernet0/1     <not set>

# Router1
FastEthernet0/0     172.16.0.3/16
FastEthernet0/1     <not set>

# Router2
FastEthernet0/0     172.16.0.4/16
FastEthernet0/1     <not set>
```