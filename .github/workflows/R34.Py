import telebot
import requests

API_TOKEN = '7273883700:AAHqK2k-jY6qTxRUTzzO97vuKZrAlYJGqiA'
bot = telebot.TeleBot(API_TOKEN)

API_URL = 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1'

posts = []
current_index = 0

def fetch_posts(tag=None):
    global posts
    url = API_URL
    if tag:
        url += f"&tags={tag}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            posts = response.json()
            return True
        except ValueError:
            return False  
    return False 

def fetch_post_by_id(post_id):
    url = f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&id={post_id}&json=1'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None 
    return None

def get_post(index):
    global posts
    while index < len(posts):
        post = posts[index]
        if 'file_url' in post and post['file_url']:
            return post
        index += 1
    return None

@bot.message_handler(commands=['R34'])
def handle_new_post(message):
    global current_index
    tag = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if fetch_posts(tag):
        if posts: 
            current_index = 0  
            send_post(message.chat.id)
       
    else:
        bot.send_message(message.chat.id, " ")

def send_post(chat_id):
    global current_index
    post = get_post(current_index)

    if post is None:
        bot.send_message(chat_id, " ")
        return

    caption = f"ɪᴅ - {post['id']}\n"
    file_url = post['file_url']
    
    try:
        if file_url.endswith('.gif'):
            bot.send_animation(chat_id, file_url, caption=caption, reply_markup=generate_navigation_keyboard())
        elif file_url.endswith(('.mp4', '.webm')):
            bot.send_video(chat_id, file_url, caption=caption, reply_markup=generate_navigation_keyboard())
        else:
            bot.send_photo(chat_id, file_url, caption=caption, reply_markup=generate_navigation_keyboard())
    except telebot.apihelper.ApiTelegramException as e:
        print(f" : {e}")
        current_index += 1  
        send_post(chat_id)

@bot.message_handler(commands=['R34T'])
def handle_post_tags(message):
    try:
        post_id = int(message.text.split()[1])
        post_data = fetch_post_by_id(post_id)
        if post_data and isinstance(post_data, list) and len(post_data) > 0:
            tags = post_data[0].get('tags', 'ᴛᴀɢs X')
            formatted_tags = ', '.join(tag.capitalize() for tag in tags.split())
            bot.send_message(message.chat.id, f"ᴛᴀɢs ɪᴅ {post_id}: {formatted_tags}")
        else:
            bot.send_message(message.chat.id, " ")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, " ")

@bot.message_handler(commands=['R34P'])
def handle_post_by_id(message):
    try:
        post_id = int(message.text.split()[1])
        post_data = fetch_post_by_id(post_id)
        if post_data and isinstance(post_data, list) and len(post_data) > 0:
            post = post_data[0]
            caption = f"ɪᴅ - {post['id']}\n"
            file_url = post['file_url']
            
            try:
                if file_url.endswith('.gif'):
                    bot.send_animation(message.chat.id, file_url, caption=caption)
                elif file_url.endswith(('.mp4', '.webm')):
                    bot.send_video(message.chat.id, file_url, caption=caption)
                else:
                    bot.send_photo(message.chat.id, file_url, caption=caption)
            except telebot.apihelper.ApiTelegramException as e:
                bot.send_message(message.chat.id, f" : {e}")
        else:
            bot.send_message(message.chat.id, " ")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, " ")

def generate_navigation_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    if current_index > 0:
        prev_button = telebot.types.KeyboardButton("<")
        keyboard.add(prev_button)

    if current_index < len(posts) - 1:
        next_button = telebot.types.KeyboardButton(">")
        keyboard.add(next_button)

    return keyboard

@bot.message_handler(commands=['R34S'])
def handle_command_list(message):
    commands = (
        "/R34 - ᴨоᴧучиᴛь ᴄᴀʍый ноʙый ᴨоᴄᴛ\n"
        "/R34 [ TAG ] - ᴨоᴧучиᴛь ноʙый ᴨоᴄᴛ ᴨо ᴛᴇᴦу\n"
        "/R34T [ ID ] - ᴨоᴧучиᴛь ᴛᴇᴦи ᴨоᴄᴛᴀ ᴨо ɪᴅ\n"
        "/R34P [ ID ] - ᴨоᴧучиᴛь ᴨоᴄᴛ ᴨо ɪᴅ\n"
        "/R34S - ᴨоᴋᴀзᴀᴛь ᴄᴨиᴄоᴋ ᴋоʍᴀнд"
    )
    bot.send_message(message.chat.id, f"ᴄᴨиᴄоᴋ ᴋоʍᴀнд:\n{commands}")

@bot.message_handler(func=lambda message: True)
def handle_navigation(message):
    global current_index
    if message.text == "<":
        if current_index > 0:
            current_index -= 1
            send_post(message.chat.id)
        else:
            bot.send_message(message.chat.id, " ")

    elif message.text == ">":
        if current_index < len(posts) - 1:
            current_index += 1
            send_post(message.chat.id)
        else:
            bot.send_message(message.chat.id, " ")

bot.polling(none_stop=True)
