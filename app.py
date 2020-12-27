from flask import Flask, request, jsonify

from services.TelnetClient import TelnetClient

app = Flask(__name__)


# telnet登陆设备
@app.route('/login', methods=['POST'])
def login_host():
    # 从form-data中获取设备编号, ip, 密码
    dev_no = request.form['dev_no']
    ip = request.form['ip']
    pwd = request.form['pwd']

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
    # 从form-data中获取设备编号
    dev_no = request.form['dev_no']

    device = get_device(dev_no)
    # 登出成功返加true，否则返回false
    if dev_no is not None:
        is_succeed, msg = device.logout_host()
    else:
        is_succeed = False
        msg = '不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 查看路由表和路由协议
@app.route('/show_info', methods=['POST'])
def show_info():
    # 从form-data中获取设备编号
    dev_no = request.form['dev_no']
    device = get_device(dev_no)
    # 执行命令
    route = device.execute_command('show ip route')
    protocol = device.execute_command('show ip protocols')
    result = {'state': True, 'route': route, 'protocol': protocol}
    return jsonify(result)


# 配置RIP动态路由
@app.route('/config_rip', methods=['POST'])
def config_rip():
    # 从form-data中获取特权密码
    en_pwd_r0 = request.form['en_pwd_r0']
    en_pwd_r1 = request.form['en_pwd_r1']
    en_pwd_r2 = request.form['en_pwd_r2']

    is_succeed_r0, msg_r0 = router0.config_rip(['172.16.0.0', '172.17.0.0'], en_pwd_r0)
    is_succeed_r1, msg_r1 = router1.config_rip(['172.16.0.0', '172.17.0.0', '172.18.0.0'], en_pwd_r1)
    is_succeed_r2, msg_r2 = router2.config_rip(['172.16.0.0', '172.18.0.0'], en_pwd_r2)

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# 配置OSPF协议
@app.route('/config_ospf', methods=['POST'])
def config_ospf():
    # 从form-data中获取特权密码
    en_pwd_r0 = request.form['en_pwd_r0']
    en_pwd_r1 = request.form['en_pwd_r1']
    en_pwd_r2 = request.form['en_pwd_r2']

    is_succeed_r0, msg_r0 = router0.config_ospf(en_pwd_r0, ['172.16.0.0', '172.17.0.0'], ['0', '0'], '0.0.255.255')
    is_succeed_r1, msg_r1 = router1.config_ospf(en_pwd_r1, ['172.16.0.0', '172.17.0.0', '172.18.0.0'], ['0', '0', '0'], '0.0.255.255')
    is_succeed_r2, msg_r2 = router2.config_ospf(en_pwd_r2, ['172.16.0.0', '172.18.0.0'], ['0', '0'], '0.0.255.255')

    is_succeed = is_succeed_r0 and is_succeed_r1 and is_succeed_r2
    msg = msg_r0 + ', ' + msg_r1 + ', ' + msg_r2
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
