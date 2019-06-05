import unittest

from Common.Email import *
from Framework import *


class Email(unittest.TestCase):
    @unittest.skip
    def test_send_mail(self):
        smtp_info = {'server': 'smtp.163.com',
                     'port': '25',
                     'username': 'alex_chen_wesoft@163.com',
                     'password': 'Wesoft123'}
        send_content = {'send_from': 'alex_chen_wesoft@163.com',
                        'send_to': 'alex.chen@wesoft.com',
                        'subject': 'test email',
                        'text': '这是一封测试邮件，收到请忽略！'}
        send_to = ['alex.chen@wesoft.com']
        send_mail(smtp_info, send_content, send_to)

    # @unittest.skip
    def test_email_result(self):
        devices_list = [{'deviceName': 'Chrome',
                         'devicePlatform': 'Chrome',
                         'udid': 'None',
                         'platformVersion': 'None',
                         'app': 'None',
                         'ScheduleTime': None}]
        devices = prepare(devices_list)
        appium_server = AppiumServer(devices)
        appium_server.start_server()
        devices = [dev for dev in devices if dev['deviceName']
                   not in appium_server.interrupt]
        excel_instant = exExcel(CONST.EXCELPATH, data_only=True)
        email_result(devices, excel_instant)
