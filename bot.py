import telebot

token = '479204960:AAHVGrW6jzi1xSegLtAFOlpII9ouy7tkJFg'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    answer = "Спасибо за внимание ко мне. Я польщён из локалки"
    bot.send_message(message.chat.id, answer)

if __name__ == '__main__':
    print('It works!')
    bot.polling(none_stop=True)