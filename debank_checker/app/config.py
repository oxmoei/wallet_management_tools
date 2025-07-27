from loguru import logger
from sys import stderr

BLACK_COLOR = False     # 如果表格显示不正确，则更改为 True
SLEEP_TIME = 1.5       # 如果出现“TOO MANY REQUESTS”错误，请在此处增加请求之间的休眠时间
NODE_SLEEP_TIME = 0.2   # 如果你的电脑很卡，请增加这个值。

import os
# 确保可以从任何路径运行时都能正确引用 js/main.js、balances.json、logs/log.log
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_js = os.path.join(BASE_DIR, 'js', 'main.js')
file_json = os.path.join(BASE_DIR, 'balances.json')
file_log = os.path.join(BASE_DIR, 'logs', 'log.log')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
# 如需另外输出日志文件，请消除注释下行代码
# logger.add(file_log, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
