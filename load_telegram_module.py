import subprocess
import sys
import json
import os

'''
COPIAR ESTE ARQUIVO PARA A PASTA DO PROJETO E USÁ-LO PARA CARREGAR O MÓDULO DO TELEGRAM:
-> from load_telegram_module import TelegramAPI, TelegramUtils
'''

print("\nCarregando o módulo remoto do Telegram\n\n")


def find_git_root_path():
    try:
        # Run the git command to get the top-level directory
        git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT).strip()
        return git_root.decode('utf-8')
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erro: Não é um repositório git. ({e.output})")

def find_tg_credentials_path():
    '''
    Finds the path of the file 'telegram_credentials.json' within the project.
    '''
    original_wd = os.getcwd()
    git_root = find_git_root_path()
    os.chdir(git_root)
    path = None

    for root, dirs, files in os.walk('.'):
        if 'telegram_credentials.json' in files:
            path = os.path.join(root, 'telegram_credentials.json')
            path = os.path.abspath(path)
            break
    
    os.chdir(original_wd)
    
    if not path:
        raise Exception("Arquivo 'telegram_credentials.json' não encontrado no repositório git.")
    
    return path

def install_and_import_module():
    '''
    Ensures the running program uses the latest version of the module from GitHub.
    '''
    # dynamically define the pip command to be used according to the environment
    pip_command = [sys.executable, '-m', 'pip']

    # Force reinstall of the module from GitHub
    commands = pip_command + ['install', '--force-reinstall', '--no-cache-dir', 'git+https://github.com/victorccaldas/telegram-api.git']
    subprocess.run(commands)

    # Now import the remote module
    from telegram_api import TelegramAPI, TelegramUtils

    return TelegramAPI, TelegramUtils

def initiate_credentials(TelegramAPI, TelegramUtils):
    # load the telegram credentials
    with open(find_tg_credentials_path(), 'r') as f:
        data = json.load(f)
        apikey = data['apikey']
        meuid = data['meuid']
        groupid = data['groupid']

    TelegramAPI = TelegramAPI(apikey, meuid, groupid)
    TelegramUtils = TelegramUtils(TelegramAPI)

    return TelegramAPI, TelegramUtils

TelegramAPI, TelegramUtils = install_and_import_module()
TelegramAPI, TelegramUtils = initiate_credentials(TelegramAPI, TelegramUtils)

print('\n\n')
