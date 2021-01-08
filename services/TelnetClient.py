import logging
import telnetlib
import time

from IPy import IP


class TelnetClient:
    name = 'default'
    host_ip = '127.0.0.1'
    telnet_pwd = 'cisco'
    enable_pwd = 'cisco'

    def __init__(self, name='default'):
        logging.basicConfig(level=logging.NOTSET)  # 设置日志级别
        self.name = name
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
            msg = '网络连接失败'
            logging.warning(ip + ':' + msg)
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
            msg = self.name + '登录成功'
            # 登陆成功，则记录设备的ip和密码
            self.host_ip = ip
            self.telnet_pwd = password
            logging.info(self.name + ':' + ip + ':' + msg)
            return True, msg
        else:
            msg = self.name + '登录失败，密码错误'
            logging.warning(self.name + ':' + ip + ':' + msg)
            return False, msg

    '''
    telnet登出设备
    '''
    def logout_host(self):
        self.tn.write(b"exit\n")
        msg = self.name + '退出登录'
        logging.info(self.host_ip + ':' + msg)
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
        logging.info('Command Result:\n%s' % result)
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
            msg = '进入特权模式'
            logging.info(self.host_ip + ':' + msg)
            # 成功则记录设备的特权密码
            self.enable_pwd = en_password
            return True, msg
        else:
            msg = '进入特权模式失败，密码错误'
            logging.warning(self.host_ip + ':' + msg)
            return False, msg

    '''
    配置串行接口
    serial_ip   串行接口IP
    mask        子网掩码
    '''
    def init_serial(self, serial_ip, mask):
        self.execute_command('configure terminal')
        for i, ip in zip(range(len(serial_ip)), serial_ip):
            # 通过ip是否为'-'判断是否要配置对应串行接口
            if len(ip) > 1:
                self.execute_command('interface s0/0/' + str(i))
                self.execute_command('ip address ' + ip + ' ' + mask)
                self.execute_command('no shutdown')
                time.sleep(2)
                self.execute_command('exit')
        self.execute_command('exit')

        msg = self.name + '串行接口配置完成'
        logging.info(self.host_ip + ':' + msg)
        return True, msg

    '''
    配置RIP协议
    networks    网络列表
    '''
    def config_rip(self, networks, mask):
        self.execute_command('configure terminal')
        self.execute_command('router rip')
        for network in networks:
            if len(network) > 1:
                self.execute_command('network ' + IP(network).make_net(mask).strNormal(0))
        self.execute_command('exit')
        self.execute_command('exit')
        msg = 'RIP配置成功'
        logging.info(self.host_ip + ':' + msg)
        return True, msg

    '''
    配置OSPF协议
    areas   区域列表，测试时可全部设为0
    mask    子网掩码
    '''
    def config_ospf(self, networks, areas, mask):
        # 计算掩码反码
        mask_list = mask.split('.')
        negative_mask = ''
        for i, m in zip(range(len(mask_list)), mask_list):
            negative_mask += str(255 - int(m))
            if i < len(mask_list) - 1:
                negative_mask += '.'
        self.execute_command('configure terminal')
        self.execute_command('router ospf 1')
        for network, area in zip(networks, areas):
            if len(network) > 1:
                self.execute_command(
                    'network ' + IP(network).make_net(mask).strNormal(0) + ' ' + negative_mask + ' area ' + area)
        self.execute_command('exit')
        self.execute_command('exit')
        msg = self.name + ':OSPF配置成功'
        logging.info(self.host_ip + ':' + msg)
        return True, msg
