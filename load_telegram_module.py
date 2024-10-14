import subprocess
import sys

'''
COPIAR ESTE ARQUIVO PARA A PASTA DO PROJETO E USÁ-LO PARA CARREGAR O MÓDULO DO TELEGRAM:
-> from load_telegram_module import TelegramAPI, TelegramUtils
'''

# Force reinstall of the module from GitHub

# dynamically define the pip command according to the environment
pip_command = [sys.executable, '-m', 'pip']

commands = pip_command + ['install', '--force-reinstall', '--no-cache-dir', 'git+https://github.com/victorccaldas/telegram-api.git']
subprocess.run(commands)

# Now import the remote module
from telegram_api import TelegramAPI, TelegramUtils
