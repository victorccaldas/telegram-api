import subprocess
import sys
import json
import os

'''
Este arquivo tem cópias. Editar O ORIGINAL que está no módulo do telegram.

COPIAR ESTE ARQUIVO PARA A PASTA DO PROJETO E USÁ-LO PARA CARREGAR O MÓDULO DO TELEGRAM:
-> from load_telegram_module import TelegramAPI, TelegramUtils

Por algum motivo o módulo fica com a versão antiga na atualização subsequente à atualização,
sendo necessário rodar o main duas vezes para que a atualização seja aplicada.
(pois a atualização do modulo ocorre na primeira execução, mas não são aplicadas pois o módulo já foi importado)
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

def install_and_import_module(force_reinstall:bool=True):
    '''
    Ensures the running program uses the latest version of the module from GitHub.
    '''
    # dynamically define the pip command to be used according to the environment
    pip_command = [sys.executable, '-m', 'pip']

    # check if the module is already installed
    try:
        # Try to import the module
        from telegram_api import TelegramAPI, TelegramUtils
        module_is_installed = True
    except ImportError as e:
        module_is_installed = False

    if force_reinstall or not module_is_installed:
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


# Don't force-reinstall if running system is Windows (development environment)
force_reinstall = False if os.name == 'nt' else True
# caso eu precise atualizar no windows, basta substituir o arquivo em 'AppData\Local\Programs\Python\Python311\Lib\site-packages\'

TelegramAPI, TelegramUtils = install_and_import_module(force_reinstall)
TelegramAPI, TelegramUtils = initiate_credentials(TelegramAPI, TelegramUtils)

print('Módulo do Telegram carregado.\n\n')
