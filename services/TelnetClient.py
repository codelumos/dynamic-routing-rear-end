import logging
import telnetlib
import time


class TelnetClient:
    host_ip = '127.0.0.1'
    telnet_pwd = 'cisco'
    enable_pwd = 'cisco'

    def __init__(self):
        logging.basicConfig(level=logging.NOTSET)
        self.tn = telnetlib.Telnet()

    '''
    telnet登录设备
    ip          设备IP
    password    telnet密码
    '''
    def login_host(self, ip, password):
        try:
            self.tn.open(ip, port=23)
        except:
            msg = ip + ':网络连接失败'
            logging.warning(msg)
            return False, msg
        # 等待Password出现后输入密码，最多等待10秒
        self.tn.read_until(b'Password: ', timeout=10)
        self.tn.write(password.encode('ascii') + b'\n')
        # 延时两秒再读取返回结果，给服务端足够响应时间
        time.sleep(2)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        login_result = self.tn.read_very_eager().decode('ascii')
        # 当密码错误时，会提示再次输入密码，以此来判断密码错误
        if 'Password:' not in login_result:
            msg = ip + ':登录成功'
            # 登陆成功，则记录设备的ip和密码
            self.host_ip = ip
            self.telnet_pwd = password
            logging.info(msg)
            return True, msg
        else:
            msg = ip + ':登录失败，密码错误'
            logging.warning(msg)
            return False, msg

    '''
    telnet登出设备
    '''
    def logout_host(self):
        self.tn.write(b"exit\n")
        msg = self.host_ip + ':登出'
        logging.info(msg)
        return True, msg

    '''
    执行命令，并输出执行结果
    command     命令语句
    '''
    def execute_command(self, command):
        # 执行命令
        self.tn.write(command.encode('ascii') + b'\n')
        time.sleep(2)
        # 获取命令结果
        result = self.tn.read_very_eager().decode('ascii')
        logging.info('命令执行结果:\n%s' % result)
        return result

    '''
    进入特权模式
    en_password     特权密码
    '''
    def enable(self, en_password):
        self.execute_command('enable')
        self.tn.read_until(b'Password: ', timeout=10)
        self.tn.write(en_password.encode('ascii') + b'\n')
        # 延时两秒再读取返回结果，给服务端足够响应时间
        time.sleep(2)
        enable_result = self.tn.read_very_eager().decode('ascii')
        if 'Password:' not in enable_result:
            msg = self.host_ip + ':已进入特权模式'
            # 成功则记录设备的特权密码
            self.enable_pwd = en_password
            return True, msg
        else:
            msg = self.host_ip + ':进入特权模式失败'
            logging.warning(msg)
            return False, msg

    '''
    配置串行接口
    serial_ip   串行接口IP
    mask        子网掩码
    '''
    def init_serial(self, serial_ip, mask):
        self.execute_command('configure terminal')
        for i, ip in zip(range(len(serial_ip)), serial_ip):
            # 通过ip是否为空判断是否要配置对应serial口
            if len(ip) > 1:
                self.execute_command('interface s0/0/' + str(i))
                self.execute_command('ip address ' + ip + ' ' + mask)
                self.execute_command('no shutdown')
                time.sleep(2)
                self.execute_command('exit')
        self.execute_command('exit')

        msg = self.host_ip + ':串行接口配置完成'
        return True, msg

    '''
    配置RIP协议
    networks    网络列表
    '''
    def config_rip(self, networks):
        self.execute_command('configure terminal')
        self.execute_command('router rip')
        for network in networks:
            self.execute_command('network ' + network)
        self.execute_command('exit')
        self.execute_command('exit')
        msg = self.host_ip + ':RIP配置完成'
        return True, msg

    '''
    配置OSPF协议
    areas   区域列表，测试时可全部设为0
    mask    掩码补码，0.0.255.255
    '''
    def config_ospf(self, networks, areas, mask):
        self.execute_command('configure terminal')
        self.execute_command('router ospf 1')
        for network, area in zip(networks, areas):
            self.execute_command('network ' + network + ' ' + mask + ' area ' + area)
        self.execute_command('exit')
        self.execute_command('exit')
        msg = self.host_ip + ':OSPF配置完成'
        return True, msg
