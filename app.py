import json
import logging

from flask import Flask, request, jsonify
from flask_cors import *

from services.TelnetClient import TelnetClient

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
    try:
        device = get_device(dev_no)
        # 登录成功返加true，否则返回false
        if device is not None:
            is_succeed, msg = device.login_host(ip, pwd)
        else:
            is_succeed = False
            msg = '不支持的设备'
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '登陆失败'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# telnet登出设备
@app.route('/logout', methods=['POST'])
def telnet_logout():
    data = json.loads(request.get_data())
    logging.info('Logout:' + str(data))
    # 获取设备编号
    dev_no = data['dev_no']
    try:
        device = get_device(dev_no)
        # 登出成功返加true，否则返回false
        if device is not None:
            is_succeed, msg = device.logout_host()
        else:
            is_succeed = False
            msg = '不支持的设备'
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '登出失败'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 进入特权模式
@app.route('/enable', methods=['POST'])
def enable():
    data = json.loads(request.get_data())
    logging.info('Enable:' + str(data))
    try:
        # 执行配置命令
        is_succeed_r0, info_r0 = router0.enable(data['pwd_r0'])
        is_succeed_r1, info_r1 = router1.enable(data['pwd_r1'])
        is_succeed_r2, info_r2 = router2.enable(data['pwd_r2'])
        # 返回信息
        is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
        if is_succeed:
            msg = '进入特权模式'
        else:
            msg = '进入特权模式失败'
        info = 'Router0>' + info_r0 + '\nRouter1>' + info_r1 + '\nRouter2>' + info_r2
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '后端运行错误'
        info = 'Error'

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 配置串行接口
@app.route('/init', methods=['POST'])
def init_serial():
    """
    前端传递数据格式
    {
        "r0": {
            "serial_ip": ["1.1.1.1", "2.2.2.2"],
            "mask": "255.255.0.0"
        }
    }
    """
    data = json.loads(request.get_data())
    logging.info('Init Serial:' + str(data))
    # 获取各个路由器配置信息，包括串行接口IP、子网掩码
    r0 = data['r0']
    r1 = data['r1']
    r2 = data['r2']
    try:
        # 执行配置命令
        is_succeed_r0, info_r0 = router0.init_serial(r0['serial_ip'], r0['mask'])
        is_succeed_r1, info_r1 = router1.init_serial(r1['serial_ip'], r1['mask'])
        is_succeed_r2, info_r2 = router2.init_serial(r2['serial_ip'], r2['mask'])
        # 返回信息
        is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
        if is_succeed:
            msg = '配置串行接口成功'
        else:
            msg = '配置串行接口失败'
        info = 'Router0#' + info_r0 + '\nRouter1#' + info_r1 + '\nRouter2#' + info_r2
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '后端运行错误'
        info = 'Error'

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 查看路由表和路由协议
@app.route('/info', methods=['POST'])
def show_info():
    data = json.loads(request.get_data())
    logging.info('Show info:' + str(data))
    # 获取设备编号
    dev_no = data['dev_no']
    try:
        device = get_device(dev_no)
        # 执行命令
        route = device.execute_command('show ip route')
        protocol = device.execute_command('show ip protocols')
        is_succeed = True
        msg = get_protocol(protocol)
        info = {'route': device.name + '>' + route, 'protocol': device.name + '>' + protocol}
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '后端运行错误'
        info = {'route': 'Error', 'protocol': 'Error'}

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 配置RIP协议
@app.route('/config/rip', methods=['POST'])
def config_rip():
    data = json.loads(request.get_data())
    logging.info('Config RIP:' + str(data))
    # 获取各个路由器配置信息，包括串行接口IP、子网掩码
    r0 = data['r0']
    r1 = data['r1']
    r2 = data['r2']
    try:
        is_succeed_r0, info_r0 = router0.config_rip(['172.16.0.0', r0['serial0'], r0['serial1']], r0['mask'])
        is_succeed_r1, info_r1 = router1.config_rip(['172.16.0.0', r1['serial0'], r1['serial1']], r1['mask'])
        is_succeed_r2, info_r2 = router2.config_rip(['172.16.0.0', r2['serial0'], r2['serial1']], r2['mask'])
        is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
        if is_succeed:
            msg = 'RIP协议配置成功'
        else:
            msg = 'RIP协议配置失败'
        info = 'Router0#' + info_r0 + '\nRouter1#' + info_r1 + '\nRouter2#' + info_r2
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '后端运行错误'
        info = 'Error'

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 配置OSPF协议
@app.route('/config/ospf', methods=['POST'])
def config_ospf():
    data = json.loads(request.get_data())
    logging.info('Config OSPF:' + str(data))
    # 获取各个路由器配置信息，包括串行接口IP、子网掩码
    r0 = data['r0']
    r1 = data['r1']
    r2 = data['r2']
    try:
        is_succeed_r0, info_r0 = router0.config_ospf(['172.16.0.0', r0['serial0'], r0['serial1']], ['0', '0'],
                                                     r0['mask'])
        is_succeed_r1, info_r1 = router1.config_ospf(['172.16.0.0', r1['serial0'], r1['serial1']], ['0', '0', '0'],
                                                     r1['mask'])
        is_succeed_r2, info_r2 = router2.config_ospf(['172.16.0.0', r2['serial0'], r2['serial1']], ['0', '0'],
                                                     r2['mask'])

        is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
        if is_succeed:
            msg = 'OSPF协议配置成功'
        else:
            msg = 'OSPF协议配置失败'
        info = 'Router0#' + info_r0 + '\nRouter1#' + info_r1 + '\nRouter2#' + info_r2
    except Exception as e:
        logging.error(e)
        is_succeed = False
        msg = '后端运行错误'
        info = 'Error'

    result = {'state': is_succeed, 'msg': msg, 'info': info}
    return jsonify(result)


# 配置BGP协议（仅测试）
@app.route('/config/bgp', methods=['POST'])
def config_bgp():
    data = json.loads(request.get_data())
    logging.info('Config BGP:' + str(data))
    # 获取各个路由器配置信息，包括串行接口IP、子网掩码
    r0 = data['r0']
    r1 = data['r1']
    r2 = data['r2']

    is_succeed_r0, info_r0 = router0.config_bgp(['172.16.0.0', r0['serial0'], r0['serial1']], r0['mask'])
    is_succeed_r1, info_r1 = router1.config_bgp(['172.16.0.0', r1['serial0'], r1['serial1']], r1['mask'])
    is_succeed_r2, info_r2 = router2.config_bgp(['172.16.0.0', r2['serial0'], r2['serial1']], r2['mask'])
    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    if is_succeed:
        msg = 'BGP协议配置成功'
    else:
        msg = 'BGP协议配置失败'

    info = 'Router0#' + info_r0 + '\nRouter1#' + info_r1 + '\nRouter2#' + info_r2
    result = {'state': is_succeed, 'msg': msg, 'info': info}
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
