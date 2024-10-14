import subprocess
import platform

'''
COPIAR ESTE ARQUIVO PARA A PASTA DO PROJETO E USÁ-LO PARA CARREGAR O MÓDULO DO TELEGRAM:
-> from load_telegram_module import TelegramAPI, TelegramUtils
'''

# Determine the operating system
    # se tiver no windows, iniciar com 'pip'; mas se for linux, iniciar com 'pip3.11' (devido ao meu setup de infra atual)
if platform.system() == 'Windows':
    start_commands = ['pip']
else:
    start_commands = ['pip3.11']

# Force reinstall of the module from GitHub
commands = start_commands + ['install', '--force-reinstall', '--no-cache-dir', 'git+https://github.com/victorccaldas/telegram-api.git']
subprocess.run(commands)

# Now import the remote module
from telegram_api import TelegramAPI, TelegramUtils
