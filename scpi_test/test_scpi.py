import time
import pyvisa
import numpy as np
import datetime


class SCPI:
    # 参数对应表
    ctrlbandidx = {0: "2G4", 1: "5G"}
    txmode = {0: '802.11b', 1: '802.11g', 2: '802.11n', 4: '802.11ac', 8: '802.11ax'}
    txbw = {0: '20', 1: '40', 2: '80', 5: '160'}
    txant = {1: '1', 2: '2', 4: '3'}
    res = []

    # 初始化生成连接通道
    def __init__(self):
        # 获取当前时间
        now_time = datetime.datetime.now()
        # 格式化时间字符串
        self.now_time = now_time.strftime("%Y-%m-%d-%H-%M-%S")

        rm = pyvisa.ResourceManager()
        self.my_instrument = rm.open_resource('TCPIP0::192.168.100.254::hislip0::INSTR')

    # 初始化IQ仪器设置
    def init_scpi(self, ctrlbandidx, channel, txbw):
        self.my_instrument.write('ROUT1;PORT:RES:ADD RF1A,VSA1')
        self.my_instrument.write('MEMory:TABLe:LOSS:LOAD "RF_TABLE3"')
        self.my_instrument.write('VSA1;RFC:USE "RF_TABLE3",RF1A\n\
                            VSG1;RFC:USE "RF_TABLE3",RF1A\n\
                            VSA1;RFC:USE "RF_TABLE3",RF2A\n\
                            VSG1;RFC:USE "RF_TABLE3",RF2A\n\
                            VSA1;RFC:USE "RF_TABLE3",RF3A\n\
                            VSG1;RFC:USE "RF_TABLE3",RF3A\n\
                            VSA1;RFC:USE "RF_TABLE3",RF4A\n\
                            VSG1;RFC:USE "RF_TABLE3",RF4A')
        self.my_instrument.write('MEMory:TABLe "RF_TABLE3";MEMory:TABLe:STORe')
        self.my_instrument.write('CHAN1;WIFI')
        self.my_instrument.write('CHAN1;WIFI;CONF:chan:BAND {}'.format(self.ctrlbandidx[ctrlbandidx]))
        self.my_instrument.write('CHAN1;CHAN1;WIFI;CONF:CHAN:IND1 {}'.format(channel))
        # 选择 带宽
        self.my_instrument.write('CHAN1;WIFI;CONF:CHAN:CBW {}000000'.format(self.txbw[txbw]))
        self.my_instrument.write('CHAN1;WIFI; HSET:ALL VSA1')
        # 如果带宽为40，中心偏移-10
        if txbw == 1:
            self.my_instrument.write('CHAN1;WIFI;CONF:CHAN:CBW 20000000')
            self.my_instrument.write('CHAN1;WIFI; HSET:ALL VSA1')
            self.my_instrument.write('CHAN1;WIFI;CONF:CHAN:CBW {}000000'.format(self.txbw[txbw]))
        # print('线损文件:"RF_TABLE3"  mode:{} channel:{}'.format(ctrlbandidx, channel))

    # 读取IQ仪器返回的参数值并存入类中定义的res列表中
    def read_data(self, ctrlbandidx, txmode, txbw, txant, channel):
        power = []
        evm = []
        fre = []
        res = []
        while True:
            self.my_instrument.write('VSA1;RLEVel:AUTO')
            time.sleep(0.2)
            temp = self.my_instrument.query_ascii_values("VSA1;init;WIFI;calc:pow 0,1;calc:txq 0,1;FETC:POW?")
            temp1 = self.my_instrument.query_ascii_values("FETC:TXQ:OFDM?")
            print(temp)
            print(temp1)
            if len(evm) < 5:
                if temp[0] == 0.0 and temp1[0] == 0.0 and temp[1] > 0:
                    print(temp)
                    print(temp1)
                    power.append(temp[1])
                    evm.append(temp1[1])
                    fre.append(temp1[4])
            else:
                res.append(np.average(power))
                res.append(np.average(evm))
                res.append(np.average(fre))

                log1 = '线损文件:"RF_TABLE3 "' + '模式：' + str(self.ctrlbandidx[ctrlbandidx]) + ' 协议：' + str(
                        self.txmode[txmode]) + \
                       ' 带宽：' + str(self.txbw[txbw]) + ' 天线：' + str(self.txant[txant]) + ' 信道：' + str(channel)

                print(log1)
                self.write_log(log1, self.now_time)

                log2 = '功率 =' + str(res[0]) + ' evm =' + str(res[1]) + ' 频偏 =' + str(res[2])
                print(log2)
                self.write_log(log2, self.now_time)
                self.res = res
                return res

    # 检测频偏是否合格
    def check_fre(self):
        temp = self.res[2] - 0
        if temp > 1 or temp < -1:
            return temp
        else:
            self.write_log("频偏合格", self.now_time)
            return 0

    # 检测功率是否合格
    def check_pow(self, powmin, powmax):
        temp = self.res[0] - (powmin + powmax) / 2.0
        offset = (powmax - powmin) / 2.0
        offset1 = (powmin - powmax) / 2.0
        if offset1 < temp < offset:
            self.write_log("功率合格", self.now_time)
            return 0
        else:
            return temp

    # 创建日志文件并存入执行命令和结果
    def write_log(self, log, now_time):
        path = './log/' + now_time + 'log.txt'
        with open(path, 'a') as f:
            f.write(log + '\n')
            f.close()

    # 自动化测试开始前，测试是否参数比较好，没有外力影响 如：线没有连接好
    def check_data(self):
        print("请检查读取参数是否正常\n")
        for x in range(10):
            time.sleep(0.5)
            self.my_instrument.query_ascii_values("VSA1;init;WIFI;calc:pow 0,1;calc:txq 0,1")
            self.my_instrument.write('VSA1;RLEVel:AUTO')
            time.sleep(0.5)
            temp = self.my_instrument.query_ascii_values("VSA1;init;WIFI;calc:pow 0,1;calc:txq 0,1;FETC:POW?")
            temp1 = self.my_instrument.query_ascii_values("FETC:TXQ:OFDM?")
            print('power =', temp[1], ' evm =', temp1[1], ' fre =', temp1[4])


if __name__ == '__main__':
    scpi = SCPI()
    scpi.init_scpi()
    scpi.read_data()
