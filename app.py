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
    return '动态路由后端启动，Running on http://127.0.0.1:5000/'


# telnet登陆设备
@app.route('/login', methods=['POST'])
def login_host():
    # 获取前端传递的数据
    data = json.loads(request.get_data())
    logging.info('Login:' + str(data))
    # 设备编号, ip, 密码
    dev_no = data['dev_no']
    ip = data['ip']
    pwd = data['pwd']

    device = get_device(dev_no)
    # 登录成功返加true，否则返回false
    if dev_no is not None:
        is_succeed, msg = device.login_host(ip, pwd)
    else:
        is_succeed = False
        msg = '不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# telnet登出设备
@app.route('/logout', methods=['POST'])
def logout_host():
    data = json.loads(request.get_data())
    logging.info('Logout:' + str(data))
    # 获取设备编号
    dev_no = data['dev_no']

    device = get_device(dev_no)
    # 登出成功返加true，否则返回false
    if dev_no is not None:
        is_succeed, msg = device.logout_host()
    else:
        is_succeed = False
        msg = '不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 进入特权模式
@app.route('/enable', methods=['POST'])
def enable():
    data = json.loads(request.get_data())
    logging.info('Enable:' + str(data))

    # 执行进入特权模式命令
    is_succeed_r0, msg_r0 = router0.enable(data['pwd_r0'])
    is_succeed_r1, msg_r1 = router1.enable(data['pwd_r1'])
    is_succeed_r2, msg_r2 = router2.enable(data['pwd_r2'])

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
    result = {'state': is_succeed, 'msg': msg}
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
    info_r0 = data['r0']
    info_r1 = data['r1']
    info_r2 = data['r2']

    # 执行配置命令
    is_succeed_r0, msg_r0 = router0.init_serial(info_r0['serial_ip'], info_r0['mask'])
    is_succeed_r1, msg_r1 = router1.init_serial(info_r1['serial_ip'], info_r1['mask'])
    is_succeed_r2, msg_r2 = router2.init_serial(info_r2['serial_ip'], info_r2['mask'])

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
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
    # 执行命令
    route = device.execute_command('show ip route')
    protocol = device.execute_command('show ip protocols')
    result = {'state': True, 'route': route, 'protocol': protocol}
    return jsonify(result)


# 配置RIP协议
@app.route('/config/rip', methods=['POST'])
def config_rip():
    data = json.loads(request.get_data())
    logging.info('Config RIP:' + str(data))

    is_succeed_r0, msg_r0 = router0.config_rip(['172.16.0.0', '172.17.0.0'])
    is_succeed_r1, msg_r1 = router1.config_rip(['172.16.0.0', '172.17.0.0', '172.18.0.0'])
    is_succeed_r2, msg_r2 = router2.config_rip(['172.16.0.0', '172.18.0.0'])

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 配置OSPF协议
@app.route('/config/ospf', methods=['POST'])
def config_ospf():
    data = json.loads(request.get_data())
    logging.info('Config OSPF:' + str(data))

    is_succeed_r0, msg_r0 = router0.config_ospf(['172.16.0.0', '172.17.0.0'], ['0', '0'], '0.0.255.255')
    is_succeed_r1, msg_r1 = router1.config_ospf(['172.16.0.0', '172.17.0.0', '172.18.0.0'], ['0', '0', '0'],
                                                '0.0.255.255')
    is_succeed_r2, msg_r2 = router2.config_ospf(['172.16.0.0', '172.18.0.0'], ['0', '0'], '0.0.255.255')

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 配置BGP协议（仅测试）
@app.route('/config/bgp', methods=['POST'])
def config_bgp():
    data = json.loads(request.get_data())
    logging.info('Config BGP:' + str(data))
    is_succeed = True
    msg = '配置完成'
    # is_succeed = False
    # msg = '配置失败'
    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


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


if __name__ == '__main__':
    # 创建一台交换机、三台路由器
    switch2 = TelnetClient()
    router0 = TelnetClient()
    router1 = TelnetClient()
    router2 = TelnetClient()
    app.run()
