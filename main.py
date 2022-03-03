from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import os
from PIL import Image
import requests
import json
import aiogram.utils.markdown as fmt


url = 'http://127.0.0.1:8000/uploadfile_from_tg_bot?access_token=ACCESS_TOKEN&type=TYPE'


TOKEN ="YOURTOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.reply(f'Я бот. Приятно познакомиться, {msg.from_user.first_name}')

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
       await msg.answer('Привет!')
    else:
       await msg.answer('Не понимаю, что это значит.')

@dp.message_handler(content_types=["photo"])
async def download_photo(msg: types.Message):
    path = 'images'
    
    file_info =  await bot.get_file(msg.photo[0].file_id)

    print(f'file_id: {file_info.file_id}')
    print(f'file_path: {file_info.file_path}')
    print(f'file_size: {file_info.file_size}')
    print(f'file_unique_id: {file_info.file_unique_id}')

    file_name, file_extension = os.path.splitext(file_info.file_path)
    saving_path = f'./{path}/{file_info.file_id}{file_extension}'
    await msg.photo[-1].download(destination=saving_path, make_dirs=True)
    
    # await msg.reply(msg, "Фото добавлено")
    await bot.send_message(msg.from_user.id, "Изображение в обработке")
    
    files = {'file': open(saving_path, 'rb')}
    try:

        
        response = requests.post(url, files=files)
        result = json.loads(response.text)
        # print(result)
        print(f"len is: {len(result)}")

        if len(result)>1:
            
            import base64
            from PIL import Image
            from io import BytesIO

            im = Image.open(BytesIO(base64.b64decode(result['face_image'])))
            im.save('imageToSave.png', 'PNG')

            await bot.send_photo(chat_id = msg.from_user.id, photo=open('imageToSave.png', 'rb'))
            
            await msg.answer(
                fmt.text(
                    fmt.text(fmt.hunderline("ФИО"), f"{result['username']} {result['lastname']}"),
                    fmt.text(fmt.hunderline("Дата рождения: "), f"{result['birthdate']}"),
                    fmt.text(fmt.hunderline("Растояние: "), f"{result['face_disance']}"),
                    sep="\n"
                ), parse_mode="HTML"
            )
        
        else:
            await msg.answer(result)

    except requests.ConnectionError as e:
        print(e)
        await msg.answer("Сервер распознавания временно не работает!")



if __name__ == '__main__':
   executor.start_polling(dp)
    