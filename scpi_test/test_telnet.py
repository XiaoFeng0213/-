import telnetlib
import time


# host = '192.168.10.1'
# username = 'admin'
# password = 'chzhdpl@246'

class Telnet:
    # 初始化
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.tn = telnetlib.Telnet(host, port=23, timeout=10)

        self.tn.read_until(b"Login:")
        self.tn.write(username.encode('ascii') + b'\n')

        self.tn.read_until(b"Password:")
        self.tn.write(password.encode('ascii') + b'\n')

    def view(self):
        time.sleep(10)
        command_result = self.tn.read_very_eager().decode('utf-8')
        print(command_result)

    #   读取寄存器数据
    def read_data(self, wlan, loc):
        self.tn.write('clear\n'.encode('utf-8'))
        self.tn.write('iwpriv {} e2p {}\n'.format(wlan, loc).encode('utf-8'))
        time.sleep(0.5)
        out = self.tn.read_very_eager().decode('utf-8')
        jicunqi = out.split(":0x")[-1].strip().split("/ #")[0].strip()
        return jicunqi

    #   更新寄存器数据
    def update_data(self, wlan, loc, data):
        self.tn.write('iwpriv {} e2p {}={}\n'.format(wlan, loc, data).encode('utf-8'))

    #   保存寄存器数据
    def save_data(self, wlan):
        # self.tn.write('iwpriv {} set bufferWriteBack=4\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set efuseBufferModeWriteBack=1\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set bufferMode=2\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATE=TXSTOP\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATE=ATESTOP\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATE=TXSTOP\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATE=ATESTART\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATECTRLBANDIDX={}\n'.format(wlan, ctrlbandidx).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATEIPG=50\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXMODE={}\n'.format(wlan, txmode).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXMCS={}\n'.format(wlan, txmcs).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXBW={}\n'.format(wlan, txbw).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXGI={}\n'.format(wlan, txgi).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXLDPC=1\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXLEN={}\n'.format(wlan, txlen).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXANT={}\n'.format(wlan, txant).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATETXCNT=0\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATECHANNEL={}\n'.format(wlan, channel + 1).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATE=TXCOMMIT\n'.format(wlan).encode('utf-8'))
        # self.tn.write('iwpriv {} set ATE=TXFRAME\n'.format(wlan).encode('utf-8'))
        time.sleep(3)

    #   发射信号
    def shoot(self, wlan, ctrlbandidx, txmode, txmcs, txbw, txgi, txlen, txant, channel):
        self.tn.write('iwpriv {} set ATE=TXSTOP\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATE=ATESTART\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATECTRLBANDIDX={}\n'.format(wlan, ctrlbandidx).encode('utf-8'))
        self.tn.write('iwpriv {} set ATEIPG=50\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXMODE={}\n'.format(wlan, txmode).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXMCS={}\n'.format(wlan, txmcs).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXBW={}\n'.format(wlan, txbw).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXGI={}\n'.format(wlan, txgi).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXLDPC=1\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXLEN={}\n'.format(wlan, txlen).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXANT={}\n'.format(wlan, txant).encode('utf-8'))
        self.tn.write('iwpriv {} set ATETXCNT=0\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATECHANNEL={}\n'.format(wlan, channel).encode('utf-8'))
        self.tn.write('iwpriv {} set ATE=TXCOMMIT\n'.format(wlan).encode('utf-8'))
        self.tn.write('iwpriv {} set ATE=TXFRAME\n'.format(wlan).encode('utf-8'))
        time.sleep(3)

    def write_log(self, log, now_time):
        path = './log/' + now_time + 'log.txt'
        with open(path, 'a') as f:
            f.write(log + '\n')
            f.close()

# if __name__ == '__main__':
# a = Telnet(host,username,password)
# b = a.read_data('wlan4','4a2')
# c = a.read_data('wlan4','4a3')
# print(b)
# print(c)
# # a.update_data('wlan4','4a2','8081')
# a.update_data('wlan4','4a3','8080')
# a.save_data()
# c = a.read_data('wlan4','4a3')
# print(c)
# d = a.view()
