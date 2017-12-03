import requests
import json
import telebot

token = '479204960:AAHVGrW6jzi1xSegLtAFOlpII9ouy7tkJFg'
bot = telebot.TeleBot(token)

def getNkoInfo(inn):
    info = {}
    nko_url = 'http://openngo.ru/api/organizations/?inn='
    r_nko = requests.get(nko_url+inn)
    data_nko = r_nko.json()
    
    if (data_nko['count'] == 0):        
        info['presence'] = False
    else: 
        info['presence'] = True
        if 'name' in data_nko['results'][0]:
            info['name'] = data_nko['results'][0]['name']
        if 'ogrn' in data_nko['results'][0]:
            info['url'] = "https://openngo.ru/organization/" + data_nko['results'][0]['ogrn']
            info['orgn'] = data_nko['results'][0]['ogrn']
        info['inn'] = inn
        if 'type' in data_nko['results'][0]:
            info['type'] = data_nko['results'][0]['type']['name']       
        if 'active' in data_nko['results'][0]:            
            info['active'] = data_nko['results'][0]['active']
        if 'region' in data_nko['results'][0]:
            info['region'] = data_nko['results'][0]['region']['name']
        if 'money_transfers_sum' in data_nko['results'][0]: 
            info['money_transfers_sum'] = data_nko['results'][0]['money_transfers_sum'] 
        if 'money_transfers_sum_by_type' in data_nko['results'][0]: 
            info['money_transfers_sum_by_type'] = data_nko['results'][0]['money_transfers_sum_by_type']
        
        smi_url = 'http://openmassmedia.ru/api/founders/?inn='
        r_smi = requests.get(smi_url+inn)
        data_smi = r_smi.json()
        
        info['media'] = {}
      
        regNumIDs = []
        if len(data_smi['results']) > 0:
            if 'media' in data_smi['results'][0]:
                for result in data_smi['results'][0]['media']:
                    regNumIDs.append(result['reg_num_id'])
        
        for regNumID in regNumIDs:
            smi_reg_url = 'http://openmassmedia.ru/api/media/?reg_num_id='
            r_smi_reg = requests.get(smi_reg_url+regNumID)
            data_smi_reg = r_smi_reg.json()
            info['media'][data_smi_reg['results'][0]['name']] = {}
            if 'territory' in data_smi_reg['results'][0]:
                info['media'][data_smi_reg['results'][0]['name']]['territory'] = data_smi_reg['results'][0]['territory']
            if 'languages' in data_smi_reg['results'][0]:
                info['media'][data_smi_reg['results'][0]['name']]['langs'] = data_smi_reg['results'][0]['languages']
            if 'type' in data_smi_reg['results'][0]:
                info['media'][data_smi_reg['results'][0]['name']]['type'] = data_smi_reg['results'][0]['type']['name']
            if ('website' in data_smi_reg['results'][0]) and not (type(data_smi_reg['results'][0]['website']) == type(None)) :
                info['media'][data_smi_reg['results'][0]['name']]['website'] = data_smi_reg['results'][0]['website']
            info['media'][data_smi_reg['results'][0]['name']]['url'] = "https://openmassmedia.ru/media/{}/".format(regNumID)
            if 'founders' in data_smi_reg['results'][0]:
                info['media'][data_smi_reg['results'][0]['name']]['co-founders'] = []
                for founder in data_smi_reg['results'][0]['founders']:
                    if not founder['inn'] == inn:
                        info['media'][data_smi_reg['results'][0]['name']]['co-founders'].append(founder['name'])

    return info

@bot.message_handler(commands=['start']) 
def start(message): 
    answer = "Введите команду /innINFO <ИНН организации>, чтобы получить информацию об НКО и имеющихся у него СМИ"
    bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=['innINFO'])
def handle_start_help(message):
    if len(message.text.split()) == 2:
        inn = message.text.split()[1]
        org_info = getNkoInfo(inn)
        if org_info['presence'] == True:
            if 'name' in org_info:
                answer = org_info['name'] + ": \n\n"
            if 'url' in org_info:
                answer += "Ссылка на организацию: " + org_info['url'] + "\n"
            if 'money_transfers_sum_by_type' in org_info:
                answer += "Источники дохода:" + "\n"
                if 'Contract' in org_info['money_transfers_sum_by_type']:
                    answer += "    Контракты: " + str(org_info['money_transfers_sum_by_type']['Contract']) + "\n"
                if 'Grant' in org_info['money_transfers_sum_by_type']:
                    answer += "    Гранты: " + str(org_info['money_transfers_sum_by_type']['Grant']) + "\n"
                if 'Subsidy' in org_info['money_transfers_sum_by_type']:
                    answer += "    Субсидии: " + str(org_info['money_transfers_sum_by_type']['Subsidy']) + "\n"

            if (len(org_info['media']) > 0):
                if 'inn' in org_info:
                    answer += "ИНН: " + org_info['inn'] + "\n"
                if 'orgn' in org_info:
                    answer += "ОРГН: " + org_info['orgn'] + "\n"
                if 'type' in org_info:
                    answer += "Тип организации: " + org_info['type'] + "\n"
                if (org_info['active']) == True:
                    answer += "Статус организации: действующая \n"
                else:
                    answer += "Статус организации: не действующая \n"
                if 'region' in org_info:
                    answer += "Регион: " + org_info['region'] + "\n"
                answer += "СМИ НКО"
                for m in org_info['media']:
                    answer += "\n\n" + m + ": \n"
                    if 'territory' in org_info['media'][m]:
                        answer += "Территория распространения СМИ: " + org_info['media'][m]['territory'] + "\n"
                    if 'langs' in org_info['media'][m]:
                        answer += "Языки: " + org_info['media'][m]['langs'] + "\n"
                    if 'type' in org_info['media'][m]:
                        answer += "Форма выпуска: " + org_info['media'][m]['type'] + "\n"
                    if 'website' in org_info['media'][m]:
                        answer += "Сайт: " + org_info['media'][m]['website'] + "\n"
                    if 'url' in org_info['media'][m]:
                        answer += "Ссылка на СМИ: " + org_info['media'][m]['url'] + "\n"
                    if len(org_info['media'][m]['co-founders']) > 0:
                        answer += 'Соучередители: '
                        for co in org_info['media'][m]['co-founders']:
                            answer += co + ''
                        answer += "\n"
            else:
                answer += "У НКО не найдено СМИ"
        else:
            answer = "Организации с таким ИНН нет в базе НКО"
    else:
        answer = "Вы неправильно задали INN организации"
    bot.send_message(message.chat.id, answer)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
    answer = "Комнанда не распознана. Введите команду:"
    answer += "\n /innINFO <ИНН организации>, чтобы получить информацию об НКО и имеющихся у него СМИ"
    bot.send_message(message.chat.id, answer)
    


if __name__ == '__main__':
    print('It works!')
    bot.polling(none_stop=True)