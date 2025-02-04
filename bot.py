from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Substitua com as informações do seu bot
api_id = 20964711
api_hash = "f9160eb582065e9d0e5a852ff8Ocd8e9"  # Use o hash correto
bot_token = "SEU_BOT_TOKEN_AQUI"  # Coloque o token do seu bot aqui
original_bot_username = "@EmonNullbot"  # Nome do bot

# Inicializa os clientes
app = Client("my_account", api_id, api_hash)
bot = Client("my_bot", api_id, api_hash, bot_token=bot_token)

user_sessions = {}

@app.on_message(filters.private & ~filters.me)
def forward_to_bot(client, message):
    """ Captura mensagem do usuário e repassa ao bot original. """
    user_id = message.chat.id
    user_sessions[user_id] = message.message_id  
    client.send_message(original_bot_username, message.text)

@app.on_message(filters.private & filters.me)
def capture_reply(client, message):
    """ Captura resposta do bot original e repassa para o usuário final. """
    if message.reply_to_message:
        original_message_id = message.reply_to_message.message_id
        for user_id, msg_id in user_sessions.items():
            if msg_id == original_message_id:
                # Captura botões inline
                buttons = []
                if message.reply_markup and isinstance(message.reply_markup, InlineKeyboardMarkup):
                    for row in message.reply_markup.inline_keyboard:
                        button_row = [
                            InlineKeyboardButton(text=btn.text, callback_data=btn.callback_data) for btn in row
                        ]
                        buttons.append(button_row)

                # Cria o teclado inline para o usuário final
                reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

                # Reenvia a resposta do bot original com os botões
                bot.send_message(user_id, message.text, reply_markup=reply_markup)
                break

@bot.on_callback_query()
def handle_callback(client, callback_query):
    """ Captura clique no botão e repassa para o bot original. """
    user_id = callback_query.message.chat.id
    data = callback_query.data

    # Repassa a interação ao bot original via sua conta pessoal
    app.send_message(original_bot_username, data)

    # Aguarda resposta do bot original
    @app.on_message(filters.private & filters.me)
    async def handle_original_reply(client, message):
        """ Aguarda resposta do bot original e repassa para o usuário. """
        if message.reply_to_message and message.reply_to_message.text == data:
            # Captura botões inline da resposta
            buttons = []
            if message.reply_markup and isinstance(message.reply_markup, InlineKeyboardMarkup):
                for row in message.reply_markup.inline_keyboard:
                    button_row = [
                        InlineKeyboardButton(text=btn.text, callback_data=btn.callback_data) for btn in row
                    ]
                    buttons.append(button_row)

            # Cria o teclado inline para o usuário final
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

            # Reenvia resposta do bot original com botões
            await bot.send_message(user_id, message.text, reply_markup=reply_markup)

            # Remove o listener para evitar duplicação
            app.remove_handler(handle_original_reply)

# Inicia os bots
print("Bot rodando...")
app.run()
bot.run()