import json
import logging

from flask import Flask, request, jsonify
from flask_cors import *

from service.TelnetClient import TelnetClient

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域访问


# 根目录
@app.route('/')
def hello():
    logging.info('/')
    return '动态路由后端，Running on http://127.0.0.1:5000/'


# telnet登陆设备
@app.route('/login', methods=['POST'])
def telnet_login():
    # 获取前端传递的数据
    data = json.loads(request.get_data())
    logging.info('Login:' + str(data))
    # 获取设备编号, ip, 密码
    dev_no = data['dev_no']
    ip = data['ip']
    pwd = data['pwd']
    device = get_device(dev_no)
    # 登陆
    if device is not None:
        try:
            is_succeed, msg = device.login_host(ip, pwd)
        except Exception as e:
            logging.error('Login:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# telnet登出设备
@app.route('/logout', methods=['POST'])
def telnet_logout():
    data = json.loads(request.get_data())
    logging.info('Logout:' + str(data))
    # 获取设备编号
    dev_no = data['dev_no']
    device = get_device(dev_no)
    # 登出
    if device is not None:
        try:
            is_succeed, msg = device.logout_host()
        except Exception as e:
            logging.error('Logout:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 进入特权模式
@app.route('/enable', methods=['POST'])
def enable():
    data = json.loads(request.get_data())
    logging.info('Enable:' + str(data))
    # 获取设备编号, 特权密码
    dev_no = data['dev_no']
    pwd = data['pwd']
    device = get_device(dev_no)
    # 进入特权模式
    if device is not None:
        try:
            is_succeed, msg = device.enable(pwd)
        except Exception as e:
            logging.error('Enable:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 配置串行接口
@app.route('/init', methods=['POST'])
def init_serial():
    data = json.loads(request.get_data())
    logging.info('Init Serial:' + str(data))
    # 获取设备编号, 串行接口IP列表, 子网掩码
    dev_no = data['dev_no']
    ip_list = data['ip_list']
    mask = data['mask']
    device = get_device(dev_no)
    # 初始化串行接口
    if device is not None:
        try:
            is_succeed, msg = device.init_serial(ip_list, mask)
        except Exception as e:
            logging.error('Init Serial:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 查看路由表和路由协议
@app.route('/info', methods=['POST'])
def show_info():
    data = json.loads(request.get_data())
    logging.info('Show info:' + str(data))
    # 获取设备编号
    dev_no = data['dev_no']
    device = get_device(dev_no)
    # 查看信息
    if device is not None:
        try:
            device.execute_command('terminal length 0')  # 命令不分页显示
            route = device.execute_command('show ip route')
            protocol = device.execute_command('show ip protocols')
            is_succeed = True
            msg = get_protocol(protocol)
            info = {'route': device.name + '# ' + route, 'protocol': device.name + '# ' + protocol}
        except Exception as e:
            logging.error('Show info:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
            info = {'route': 'Error', 'protocol': 'Error'}
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'
        info = {'route': 'Unknown device', 'protocol': 'Unknown device'}

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 配置RIP协议
@app.route('/config/rip', methods=['POST'])
def config_rip():
    data = json.loads(request.get_data())
    logging.info('Config RIP:' + str(data))
    # 获取设备编号, 配置信息
    dev_no = data['dev_no']
    dev_data = data['dev_data']
    device = get_device(dev_no)
    # 配置RIP协议
    if device is not None:
        # 获取参数
        networks = [device.host_ip, dev_data['serial0'], dev_data['serial1']]
        # 配置协议
        try:
            is_succeed, msg = device.config_rip(networks, dev_data['mask'])
        except Exception as e:
            logging.error('Config RIP:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 配置OSPF协议
@app.route('/config/ospf', methods=['POST'])
def config_ospf():
    data = json.loads(request.get_data())
    logging.info('Config OSPF:' + str(data))
    # 获取设备编号, 配置信息
    dev_no = data['dev_no']
    dev_data = data['dev_data']
    device = get_device(dev_no)
    # 配置OSPF协议
    if device is not None:
        # 获取参数
        networks = [device.host_ip, dev_data['serial0'], dev_data['serial1']]
        if dev_no == 'r1':
            area = ['0', '0', '0']
        else:
            area = ['0', '0']
        # 配置协议
        try:
            is_succeed, msg = device.config_ospf(networks, area, dev_data['mask'])
        except Exception as e:
            logging.error('Config OSPF:' + str(e))
            is_succeed = False
            msg = device.name + ' - 服务器错误'
    else:
        is_succeed = False
        msg = dev_no + ' - 不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 获取路由协议
def get_protocol(protocol):
    if 'ospf' in protocol:
        return '当前路由协议: OSPF'
    if 'rip' in protocol:
        return '当前路由协议: RIP'
    return '尚未配置路由协议'


# 获取设备对象
def get_device(dev_no):
    if dev_no == 's2':
        return switch2
    elif dev_no == 'r0':
        return router0
    elif dev_no == 'r1':
        return router1
    elif dev_no == 'r2':
        return router2
    else:
        return None


# 程序入口
if __name__ == '__main__':
    # 创建一台交换机、三台路由器
    switch2 = TelnetClient('Switch2')
    router0 = TelnetClient('Router0')
    router1 = TelnetClient('Router1')
    router2 = TelnetClient('Router2')
    app.run()
