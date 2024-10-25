import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Отсутствует файл .env")
else:
    load_dotenv()


COOKIES = os.getenv("COOKIES")
Authorization = os.getenv("Authorization")
token = os.getenv("token")
if COOKIES is None:
    exit("COOKIES не найден в переменных окружения.")
elif Authorization is None:
    exit("Authorization не найден в переменных окружения.")
elif token is None:
    exit("token не найден в переменных окружения.")

