import inquirer
from termcolor import colored
from inquirer.themes import load_theme_from_dict as loadth

from .config import *

def get_action():
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.List(
            "action",
            message=colored("⬇⬆ 请选择选项", 'light_yellow'),
            choices=["💲 -获取钱包中所有EVM链的代币余额", "🪙 -仅获取特定代币的余额", "📖 -帮助", "📤 -退出"],
        )
    ]
    action = inquirer.prompt(question, theme=loadth(theme))['action']
    return action

def select_chains(chains):
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.Checkbox(
            "chains",
            message=colored("💁‍♀️  选择您想要获取余额的网络", 'light_yellow'),
            choices=["所有 EVM 网络", *chains],
        )
    ]
    selected_chains = inquirer.prompt(question, theme=loadth(theme))['chains']
    if ('所有 EVM 网络' in selected_chains):
        return chains
    return selected_chains

def get_ticker():
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.Text("ticker", message=colored("✍️  输入代币名称（Symbol）", 'light_yellow'))
    ]
    ticker = inquirer.prompt(question, theme=loadth(theme))['ticker'].upper()
    return ticker

def get_minimal_amount_in_usd():
    while True:
        theme = {
            "Question": {
                "brackets_color": "bright_yellow"
            },
            "List": {
                "selection_color": "bright_blue"
            }
        }

        question = [
                inquirer.Text("min_amount", message=colored("✍️  请输入最小金额（默认值：0.01美元）", 'light_yellow'), default="0.01")
        ]
        try:
            min_amount = float(inquirer.prompt(question, theme=loadth(theme))['min_amount'].strip())
            break
        except:
            logger.error('❌  错误！输入无效')
    if (min_amount) == 0:
        min_amount = -1
    return min_amount


def get_num_of_threads():
    while True:
        theme = {
            "Question": {
                "brackets_color": "bright_yellow"
            },
            "List": {
                "selection_color": "bright_blue"
            }
        }

        question = [
                inquirer.Text("num_of_threads", message=colored("✍️  工作线程数量（如果你有超过100个地址，请只设置1个线程）", 'light_yellow'), default="1")
        ]
        try:
            num_of_threads = int(inquirer.prompt(question, theme=loadth(theme))['num_of_threads'].strip())
            break
        except:
            logger.error('❌  错误！输入无效')
    if (num_of_threads) == 0:
        num_of_threads = 3
    return num_of_threads
