import logging
import telnetlib
import time


class TelnetClient:
    def __init__(self):
        self.tn = telnetlib.Telnet()

    # telnet登录主机
    def login_host(self, host_ip, password):
        try:
            # self.tn = telnetlib.Telnet(host_ip, port=23)
            self.tn.open(host_ip, port=23)
        except:
            msg = host_ip + ': 网络连接失败'
            logging.warning(msg)
            return False, msg
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
            msg = host_ip + ': 登录成功'
            logging.warning(msg)
            return True, msg
        else:
            msg = host_ip + ': 登录失败，密码错误'
            logging.warning(msg)
            return False, msg

    # 执行命令，并输出执行结果
    def execute_command(self, command):
        # 执行命令
        self.tn.write(command.encode('ascii') + b'\n')
        time.sleep(2)
        # 获取命令结果
        result = self.tn.read_very_eager().decode('ascii')
        logging.warning('命令执行结果：\n%s' % result)
        return result

    # telnet登出主机
    def logout_host(self):
        self.tn.write(b"exit\n")
        return True

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
        return True

    # 配置OSPF
    # areas区域列表，测试时可全部设为0
    # mask掩码补码，0.0.255.255
    def config_ospf(self, networks, areas, mask):
        self.execute_command('enable')
        self.tn.read_until(b'Password: ', timeout=10)
        self.tn.write('cisco'.encode('ascii') + b'\n')
        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        self.execute_command('configure terminal')
        self.execute_command('router ospf 1')
        for network, area in zip(networks, areas):
            self.execute_command('network ' + network + ' ' + mask + ' area ' + area)
        return True
