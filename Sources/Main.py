from flask import Flask, request, jsonify

from TelnetClient import TelnetClient

app = Flask(__name__)


# telnet登陆设备
@app.route('/login_host', methods=['POST'])
def login_host():
    # 从form-data中获取设备编号, ip, 密码
    device_no = request.form['device_no']
    ip = request.form['ip']
    pwd = request.form['password']

    # 登录成功返加true，否则返回false
    if device_no == 's2':
        is_succeed, msg = switch2.login_host(ip, pwd)
    elif device_no == 'r0':
        is_succeed, msg = router0.login_host(ip, pwd)
    elif device_no == 'r1':
        is_succeed, msg = router1.login_host(ip, pwd)
    elif device_no == 'r2':
        is_succeed, msg = router2.login_host(ip, pwd)
    else:
        is_succeed = False
        msg = '不支持的设备'

    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


# telnet登出设备
@app.route('/login_out', methods=['POST'])
def login_out():
    # 从form-data中获取设备编号
    device_no = request.form['device_no']
    if device_no == 's2':
        is_succeed, msg = switch2.logout_host()
    elif device_no == 'r0':
        is_succeed, msg = router0.logout_host()
    elif device_no == 'r1':
        is_succeed, msg = router1.logout_host()
    elif device_no == 'r2':
        is_succeed, msg = router2.logout_host()
    else:
        is_succeed = False
        msg = '不支持的设备'
    result = {'state': is_succeed, 'msg': msg}
    return jsonify(result)


@app.route('/show_info', methods=['POST'])
def show_info():
    ip = request.form['ip']
    pwd = request.form['password']
    # 如果登录结果返加True，则执行命令，然后退出
    login_succeed, msg = telnet_client.login_host(ip, pwd)
    if login_succeed:
        msg = telnet_client.execute_command('show ip route')
        msg += telnet_client.execute_command('show ip protocols')
        telnet_client.logout_host()
        return msg
    else:
        return msg


@app.route('/config_rip')
def config_rip():
    # router0
    if telnet_client.login_host('172.16.0.2', password):
        telnet_client.config_rip(['172.16.0.0', '172.17.0.0'])
        telnet_client.logout_host()
    # router1
    if telnet_client.login_host('172.16.0.3', password):
        telnet_client.config_rip(['172.16.0.0', '172.17.0.0', '172.18.0.0'])
        telnet_client.logout_host()
    # router2
    if telnet_client.login_host('172.16.0.4', password):
        telnet_client.config_rip(['172.16.0.0', '172.18.0.0'])
        telnet_client.logout_host()


if __name__ == '__main__':
    password = 'cisco'
    telnet_client = TelnetClient()
    switch2 = TelnetClient()
    router0 = TelnetClient()
    router1 = TelnetClient()
    router2 = TelnetClient()
    app.run()
