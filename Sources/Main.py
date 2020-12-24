from flask import Flask, request

from TelnetClient import TelnetClient

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


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
    app.run()
