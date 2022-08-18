import logging
import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import firebase_adminsdk_path, token

cred = credentials.Certificate(firebase_adminsdk_path)

firebase_admin.initialize_app(cred)
db = firestore.client()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'tlgrm-goods-service.log',
    level=logging.INFO
)


def save_chat_id(user_uid, chat_id):
    res = 'Чат успешно привязан к аккаунту. Теперь вы можете настраивать и получать уведомления об изменении цен.'

    try:
        data = db.collection('telegram_chats').where('user_uid', '==', user_uid).stream()
        exists = False

        for elem in data:            
            exists = True
            db.collection('telegram_chats').document(elem.id).update({'chat_id': chat_id})
        
        if not exists:
            db.collection('telegram_chats').add({'user_uid': user_uid, 'chat_id': chat_id})
    except:
        logging.error(f'Error while adding chat id:[{chat_id}] for user with uid:[{user_uid}]\n{traceback.format_exc()}')
        res = 'Ошибка, обратитесь, пожалуйста, к администратору. Код ошибки: 01'
    finally:
        return res


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_identification = context.args[0] if len(context.args) > 0 else -1
    logging.info(
        f'Adding user with uid:[{user_identification}] and chat_id:[{update.effective_chat.id}]')
    responce = save_chat_id(user_identification, update.effective_chat.id)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=responce)

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()
