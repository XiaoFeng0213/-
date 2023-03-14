from yaml_util import YamlUtil
import pytest
from test_telnet import Telnet
from test_scpi import SCPI


@pytest.mark.parametrize('args', YamlUtil("./test.yaml").read_yaml())
def test_calibra(args):
    # 获取参数
    ctrlbandidx = args["CTRLBANDIDX"]
    txmode = args["TXMODE"]
    txmcs = args["TXMCS"]
    txbw = args["TXBW"]
    txgi = args["TXGI"]
    txlen = args["TXLEN"]
    txant = args["TXANT"]
    channel = args["CHANNEL"]
    powmin = args["powmin"]
    powmax = args["powmax"]
    address = args["address"]
    # 获取参数
    # ctrlbandidx = 1
    # txmode = 1
    # txmcs = 7
    # txbw = 0
    # txgi = 0
    # txlen = 1024
    # txant = 1
    # channel = 36
    # powmin = 19.5
    # powmax = 20.5
    # address = '4a1'

    login = YamlUtil("./login.yaml").read_yaml()
    host = login[0]["host"]
    username = login[0]["username"]
    password = login[0]["password"]

    if ctrlbandidx == 0:
        wlan = 'wlan0'
    else:
        wlan = 'wlan4'

    # 初始化
    telnet = Telnet(host, username, password)
    scpi = SCPI()
    scpi.init_scpi(ctrlbandidx, channel, txbw)
    telnet.shoot(wlan, ctrlbandidx, txmode, txmcs, txbw, txgi, txlen, txant, channel)

    # 检查并校准
    while True:
        data = scpi.read_data(ctrlbandidx, txmode, txbw, txant, channel)
        if scpi.check_fre() == 0:
            print("频偏合格")
            break
        else:
            # 中心偏移出问题
            # 获取原参数数据
            yuan_data = telnet.read_data(wlan, 999)
            # 除去后两位的其它位
            yuan_data_1 = yuan_data[:-2]
            # 后两位
            yuan_data_2 = yuan_data[-2:]
            # 后两位转十进制
            yuan_data_2 = int(yuan_data_2, 16)
            # print('yuandata2: ', yuan_data_2)

            # 计算原数据偏移量
            if 128 <= yuan_data_2 < 192:
                bian = 128 - yuan_data_2
            elif 192 <= yuan_data_2:
                bian = yuan_data_2 - 192
            # print('bian: ', bian)

            pianyi = scpi.check_fre()
            # print('pianyi: ', pianyi)

            # telnet.tn.write(("iwpriv ra0 set ATETXFREQOFFSET=" + str(count)).encode('utf-8'))
            if pianyi > 0:
                bian = bian + 1
            elif pianyi < 0:
                bian = bian - 1
            # print("bian2: ", bian)

            if bian > 0:
                yuan_data_2 = 192 + bian
            elif bian <= 0:
                yuan_data_2 = 128 - bian
            # print("yuandata2: ", yuan_data_2)

            yuan_data_2 = str(hex(int(str(yuan_data_2), 10)))[-2:]
            # 将数据恢复
            bian_data = str(yuan_data_1) + str(yuan_data_2)
            # print('biandata: ', bian_data)

            # 修改
            telnet.update_data(wlan, 999, bian_data)
            telnet.save_data(wlan)
            telnet.shoot(wlan, ctrlbandidx, txmode, txmcs, txbw, txgi, txlen, txant, channel)
            log = "修改过程：" + "寄存器：" + "999" + "=" + yuan_data + "改成" + bian_data
            print(log)
            scpi.write_log(log, scpi.now_time)

    while True:
        data = scpi.read_data(ctrlbandidx, txmode, txbw, txant, channel)
        if scpi.check_pow(powmin, powmax) == 0:
            break
        else:
            # 获取原参数数据
            yuan_data = telnet.read_data(wlan, address)
            # 除去后两位的其它位
            yuan_data_1 = yuan_data[:-2]
            # 后两位
            yuan_data_2 = yuan_data[-2:]
            # 后两位转十进制
            yuan_data_2 = int(yuan_data_2, 16)
            # print("1yuan_data_2: ", yuan_data_2)
            # 计算原数据偏移量

            if 128 <= yuan_data_2 < 192:
                bian = 128 - yuan_data_2
            elif 192 <= yuan_data_2:
                bian = yuan_data_2 - 192
            else:
                bian = 0
            # print("bian: ", bian)

            # 获取偏移程度
            pianyi = scpi.check_pow(powmin, powmax)
            # print(pianyi)

            data_pian = int(pianyi * 2)
            # print("gaihou:", pianyi)
            # print("data_pian: ", data_pian)

            sum_pianyi_data = data_pian - bian
            # print("sun_pianyi_data: ", sum_pianyi_data)

            if sum_pianyi_data <= 0:
                yuan_data_2 = 192 - sum_pianyi_data
            elif sum_pianyi_data > 0:
                yuan_data_2 = 128 + sum_pianyi_data
            # print("yuandata_2: ", yuan_data_2)

            # 将数据偏移量转化为16进制
            yuan_data_2 = str(hex(int(str(yuan_data_2), 10)))[-2:]
            # print("16yuandata: ", yuan_data_2)

            # 将数据恢复
            bian_data = str(yuan_data_1) + str(yuan_data_2)
            # print("bian_data: ", bian_data)

            # 修改
            telnet.update_data(wlan, address, bian_data)
            telnet.save_data(wlan)
            telnet.shoot(wlan, ctrlbandidx, txmode, txmcs, txbw, txgi, txlen, txant, channel)
            log = "修改过程：" + "寄存器：" + str(address) + "=" + yuan_data + "改成" + bian_data
            print(log)
            scpi.write_log(log, scpi.now_time)


if __name__ == '__main__':
    pytest.main()
