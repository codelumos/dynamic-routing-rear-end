import logging
import telnetlib
import time


class TelnetClient:
    def __init__(self, ):
        self.tn = telnetlib.Telnet()

    # telnet登录主机
    def login_host(self, host_ip, password):
        try:
            # self.tn = telnetlib.Telnet(host_ip,port=23)
            self.tn.open(host_ip, port=23)
        except:
            logging.warning('%s网络连接失败' % host_ip)
            return False
        # 等待login出现后输入用户名，最多等待10秒
        # self.tn.read_until(b'login: ', timeout=10)
        # self.tn.write(username.encode('ascii') + b'\n')
        # 等待Password出现后输入用户名，最多等待10秒
        self.tn.read_until(b'Password: ', timeout=10)
        self.tn.write(password.encode('ascii') + b'\n')
        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        command_result = self.tn.read_very_eager().decode('ascii')
        if 'Password:' not in command_result:
            logging.warning('%s登录成功' % host_ip)
            return True
        else:
            logging.warning('%s登录失败，密码错误' % host_ip)
            return False

    # 执行命令，并输出执行结果
    def execute_command(self, command):
        # 执行命令
        self.tn.write(command.encode('ascii') + b'\n')
        time.sleep(2)
        # 获取命令结果
        command_result = self.tn.read_very_eager().decode('ascii')
        logging.warning('命令执行结果：\n%s' % command_result)

    # telnet登出主机
    def logout_host(self):
        self.tn.write(b"exit\n")

    # 配置RIP动态路由
    def config_rip(self, networks):
        self.execute_command('enable')
        self.tn.read_until(b'Password: ', timeout=10)
        self.tn.write('cisco'.encode('ascii') + b'\n')
        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        self.execute_command('configure terminal')
        self.execute_command('router rip')
        for network in networks:
            self.execute_command('network ' + network)


if __name__ == '__main__':
    password = 'cisco'

    telnet_client = TelnetClient()
    # 如果登录结果返加True，则执行命令，然后退出
    if telnet_client.login_host('172.16.0.2', password):
        telnet_client.execute_command('show ip route')
        telnet_client.execute_command('show ip protocols')
        telnet_client.logout_host()

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

    # 如果登录结果返加True，则执行命令，然后退出
    if telnet_client.login_host('172.16.0.2', password):
        telnet_client.execute_command('show ip route')
        telnet_client.execute_command('show ip protocols')
        telnet_client.logout_host()
