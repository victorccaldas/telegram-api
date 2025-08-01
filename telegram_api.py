import requests
import re
import json
from datetime import datetime
import inspect



class TelegramAPI:
    def __init__(self, api_key, personal_chat_id, group_chat_id):
        self.api_key = api_key
        self.personal_id = personal_chat_id
        self.group_id = group_chat_id

    def read(self, offset=None):
        get_updates = f'https://api.telegram.org/bot{self.api_key}/getUpdates'
        if offset:
            get_updates += f'?offset={offset}'

        r = requests.get(get_updates)
        return r.content
    
    def safe_disallow_messages_to_strangers(self, chat_id):
        
        current_id = str(chat_id)

        if not current_id == self.personal_id and not current_id == self.group_id: 
            chat_id = self.group_id

        return chat_id

    def send_file(self, file_binary, caption='', file_name='file', file_extension='.pdf', chat_id=None, allow_personal_message_only_to_self=True):

        # permite enviar msg na conversa particular apenas se o chat_id == meuid
        if allow_personal_message_only_to_self:
            chat_id = TelegramAPI.safe_disallow_messages_to_strangers(self, chat_id)

        endpoint_url = f"https://api.telegram.org/bot{self.api_key}/sendDocument?chat_id={chat_id}&caption={caption}"
        r = requests.post(endpoint_url, files={'document': (file_name+file_extension, file_binary)})
        return r

    def send_message(self, msg, parse_mode='MarkdownV2', chat_id=None, allow_personal_message_only_to_self=True):
        '''
        Usar 'send_safe_and_custom_formatted_message' para garantir uso de escapamento customizado e lidar com mensagens muito grandes.
        '''
        # permite enviar msg na conversa particular apenas se o chat_id == meuid
        if allow_personal_message_only_to_self:
            chat_id = TelegramAPI.safe_disallow_messages_to_strangers(self, chat_id)

        send_msg = f"https://api.telegram.org/bot{self.api_key}/sendMessage?chat_id={chat_id}&text={msg}"
        if parse_mode: send_msg += f"&parse_mode={parse_mode}"

        response = requests.get(send_msg)
        
        if response.status_code == 200:
            print("\n[Telegram]: ", msg, '\n')
        else:
            stack = inspect.stack()
            # The caller's frame is the second in the stack (index 1)
            caller_frame = stack[1]
            # Get the caller function's name
            caller_name = caller_frame.function

            # só retornar erro se a função que chamou for diferente de 'send_safe_and_custom_formatted_message',
            # pois essa função tem sua própria lógica de tratamento de erros
            if caller_name != 'send_safe_and_custom_formatted_message':
                error_msg = f"Erro em send_message ao enviar mensagem no Telegram:\n{response.content}"
                self.send_message(error_msg, parse_mode='', chat_id=chat_id)
                raise Exception(error_msg)
            
        return response
    
    def delete_message(self, id):
        delete_msg = f"https://api.telegram.org/bot{self.api_key}/deleteMessage?chat_id={self.group_id}&message_id={id}"
        response = requests.get(delete_msg)
        if not response.status_code == 200:
            print("Error deleting message.")
        
        return response.content
    

class TelegramUtils:
    def __init__(self, api):
        self.api = api

    def split_msg(self, text, char_limit=4096):
        all_parts = [part + '\n' for part in text.split('\n')]
        split_messages = []
        current_message = ''
        
        for new_part in all_parts:
            # add to current message if new part does not exceed the limit
                # repr() is used to count all characters, even escaping characters that would not be counted in the string length
            if len(repr(current_message)) + len(repr(new_part)) <= char_limit:
                current_message += new_part
            else:
                # if new part would exceed the limit, stash the current message and start a new one
                split_messages.append(current_message)
                current_message = new_part
        
        split_messages.append(current_message)
        return split_messages
           
    def send_safe_and_custom_formatted_message(self, og_text, parse_mode='MarkdownV2', chat_id=None, is_already_parsed=False, allow_personal_message_only_to_self=True):
        '''
        Essa função é usada pra garantir uso de escapamento customizado, e também para lidar com mensagens muito grandes.
        '''
        if parse_mode and not is_already_parsed:
            text = TelegramUtils.escape_only_wanted_characters(og_text)
        else:
            text = og_text

        response = self.api.send_message(text, parse_mode=parse_mode, chat_id=chat_id, allow_personal_message_only_to_self=allow_personal_message_only_to_self)
        json_data = json.loads(response.content.decode('utf-8'))
        
        if response.status_code != 200:
            assert 'description' in json_data, f"Erro ao enviar mensagem no Telegram: description not in json_data\nResponse: {response.content}"
            error = json_data['description']

            if "can't parse entities" in error:
                print(f'Error parsing message. Sending without parsing.')
                return TelegramUtils.send_safe_and_custom_formatted_message(self, og_text, parse_mode='', chat_id=chat_id, allow_personal_message_only_to_self=allow_personal_message_only_to_self)

            elif "is too long" in error:
                print(f'Message is too big: {len(text)} chars. Splitting into smaller chunks.')
                split_messages = TelegramUtils.split_msg(self, text=text, char_limit=4096)
                for msg in split_messages:
                    TelegramUtils.send_safe_and_custom_formatted_message(self, msg, parse_mode=parse_mode, chat_id=chat_id, is_already_parsed=True, allow_personal_message_only_to_self=allow_personal_message_only_to_self)
            
            else:
                msg = "Erro não previsto ao enviar mensagem no Telegram:" + str(response.content) +'\n\nMsg:\n' + text
                print(msg)
                return self.api.send_message(msg, parse_mode='', chat_id=chat_id, allow_personal_message_only_to_self=allow_personal_message_only_to_self)
        
        return response
        
    @staticmethod
    def escape_only_wanted_characters(text):
        '''
        OBS. Diferentemente dos outros caractéres, os '_' (underline) devem ser escapados com '/' ao invés de '\' quando utilizando em markdown,
            Pois diferente dos outros, eles são comumente usados em meio a textos ou frases sem intenção de markdown,
            o que estava causando bug na mensagem.
        '''
        def escape_markdown_v2(text):
            escape_chars = r'\*_\[\]()~>`#+-=|{}.!'
            return re.sub(r'(['+escape_chars+'])', r'\\\1', text)
            
        #text = re.escape(text) # escape special characters # removi esta parte pois junto com a função escape_markdown_v2, estava duplicadamente escaping alguns caracteres, consequentemente escaping o \ do escaping anterior e não o caractere em sí.
        text = escape_markdown_v2(text)

        # remove escaping from unwanted escapes such as markdown applications
        text = text.replace('\*', '*').replace('\ ', ' ').replace('\\n', '\n')

        # remove special escaping (utilizando '/' ao invés do padrão '\')
        text = text.replace('\/\_', '_')

        return text
    
    def ping_to_inform_activity(self):

        # load the file 'last_sent_ping_message_id.txt' if it exists
        try:
            with open('last_sent_ping_message_id.txt', 'r') as f:
                last_sent_ping_message_id = f.read()
        except FileNotFoundError:
            last_sent_ping_message_id = None

        # delete the last_sent_ping_message_id if it exists
        if last_sent_ping_message_id:
            self.api.delete_message(last_sent_ping_message_id)

        # send a new ping message
        response = self.api.send_message('Checkpoint: a execução segue ativa.', parse_mode='')
        response_dict = json.loads(response.content)
        last_sent_ping_message_id = response_dict['result']['message_id']

        # write the new last_sent_ping_message_id to the file 'last_sent_ping_message_id.txt'
        with open('last_sent_ping_message_id.txt', 'w') as f:
            f.write(str(last_sent_ping_message_id))

        return response

    def send_ping_message_every_morning_and_night(self, sent_ping_message):
        current_time = datetime.now().time()
        if (current_time >= datetime.strptime('8:00', '%H:%M').time() and current_time <= datetime.strptime('8:05', '%H:%M').time()) \
            or (current_time >= datetime.strptime('20:54', '%H:%M').time() and current_time <= datetime.strptime('20:59', '%H:%M').time()):
            if not sent_ping_message:
                TelegramUtils.ping_to_inform_activity(self)
                sent_ping_message = True
        else:
            sent_ping_message = False

        return sent_ping_message
    

if __name__ == '__main__':
    # test:
    api_key = None # your_api_key
    personal_id = None # your_personal_chat_id
    group_id = None # your_group_chat_id

    assert api_key, 'You must provide your api_key'
    assert personal_id or group_id, 'You must provide a chat_id'

    TelegramAPI = TelegramAPI(api_key, personal_id, group_id)

    TelegramUtils = TelegramUtils(TelegramAPI)

    TelegramAPI.send_message(TelegramAPI, 'test',chat_id=TelegramAPI.personal_id)

    TelegramUtils.send_safe_and_custom_formatted_message('test2', chat_id=TelegramAPI.personal_id)



