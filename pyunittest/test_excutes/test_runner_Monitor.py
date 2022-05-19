import time
import unittest
from BeautifulReport import BeautifulReport

discover = unittest.defaultTestLoader.discover("../test_case",pattern='ServicePatrol_app**.py')


nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
filename = 'Monitor测试报告'+ str(nowtime)
BeautifulReport(discover).report(description='Monitor接口测试',filename=filename,log_path="../reports")