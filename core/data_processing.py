from typing import Dict, Any
from config_data.config import *
from DataBase.db import Products
import requests
from typing import List, Optional
import openpyxl


signs = ['79f4e5dafed76aeae9d6fd3f9bda547e', 'b4ea084e04019714c29db9a4921b93f2', '57d183f51f32d0e1db5e0d930b113fee',
             'd7c6a4b897790fc357710ead60d2536f', '6991cefe113995582e577bc68de6e595', 'e4a2044db6c2daa8f62bfb4da2991c91',
             'f48a34a24473f5af464c5939773439ef', 'cf75a996a8d9e59d298966b377a26a73', '4a328ecedf895c1f85faebb05e037985',
             '50c7288fce9cd4c20173133d22d7cb6c', 'a032bf35daaab2c45adcd56d5fc26a62']


signs_price = ['441e9607039307399afab750a589876d', '09ea68ea227e76126a2a4ac1548e89d2', 'db9eeb9c75428bd6b0f56531bd42b71b',
                   '78e51ca18d4791e2a12e6ee22b380478', '102ce164db4dbe69ff6618f1cf0c29b0', '34501fb269a7c6bdbae6c4bcedffd6fc',
                   '6d112422366087e020d72d8c88498933', 'ecd91ca56a46f3a8d9ee720c8c47d4ea', '4ceceab5997830b0485f6ea813058e6c',
                   '9012718f5d5234081ba61d6e44db123e', '81e745282e75dc33b238ff1bd69ad3a3']


def get_data_price(index: int, ids: list, arr_signs=signs_price):
    """
        Получает данные о ценах для списка артикулов.

        Функция делает запрос к API для получения актуальных цен на товары,
        используя указанный знак из массива знаков.

        Аргументы:
        index (int): Индекс знака (sign) в массиве `arr_signs`, который будет использован для запроса.
        ids (list): Список артикулов (ID), для которых требуется получить данные о ценах.
        arr_signs (list): Массив знаков (signs), используемый для запросов.
                          По умолчанию используется глобальная переменная `signs_price`.

        Возвращает:
        dict: Результат запроса с данными о ценах.
    """
    try:
        # Выполняем запрос к API для получения данных о ценах
        result = get_data(type_req='price', sign=arr_signs[index], arr_articles=ids)
        return result
    except Exception as e:
        # Обработка ошибок, возникающих при выполнении запроса
        print(f"Ошибка при получении данных о ценах для индекса {index}: {e}")
        return {}




def get_data(type_req:str, sign: str, arr_articles: Optional[List[int]] = None, index: Optional[int] = None) -> dict:
    """
    Выполняет запрос на получение данных о цене или списке продуктов с сайта 4lapy.

    :param type_req: Тип запроса, например, 'price' или 'products'.
    :param sign: Подпись для аутентификации.
    :param arr_articles: (Необязательный) Список артикулов (int).
    :param index: (Необязательный) Номер страницы для пагинации.
    :return: JSON-ответ сервера.
    """

    # Общие параметры
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': Authorization,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'lapy/3.3.10 (iPhone; iOS 18.0; Scale/3.00)',
        'Cookie': COOKIES,
        'x-apps-location': 'lat:44.045160745683894,lon:43.02610139057467'
    }

    if type_req == 'price':
        url = 'https://4lapy.ru/api/v2/catalog/product/info-list/'
        data = {
            'sign': sign,
            'token': token
        }
        # Дублирование значений в 'offers'
        if arr_articles:
            data.update({f'offers[{i}]': article for i, article in enumerate(arr_articles)})

        # Выполнение POST-запроса для 'price'
        response = requests.post(url, headers=headers, data=data)

    elif type_req == 'products':
        url = 'https://4lapy.ru/api/v2/catalog/product/list/'
        params = {
            'category_id': 457,
            'count': 10,
            'page': index,
            'sign': sign,
            'sort': 'popular',
            'token': token
        }

        # Выполнение GET-запроса для 'products'
        response = requests.get(url, headers=headers, params=params)

    else:
        raise ValueError("Неверное значение type_req. Ожидается 'price' или 'products'.")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Произошла ошибка: {data} Проверьте ключ 'sign'")
        exit()





def all_data_get(signs_arr=signs):
    """
        Получает данные о продуктах из API и обрабатывает их.

        Функция выполняет запрос на получение продуктов для каждого знака (sign)
        из переданного массива `signs_arr`, обрабатывает полученные данные
        и сохраняет их в базу данных.

        Аргументы:
        signs_arr (list): Массив знаков (signs), которые используются для запросов.
                          По умолчанию используется глобальная переменная `signs`.

        Возвращает:
        None
    """

    for index, i_sig in enumerate(signs_arr):
        try:
            res = get_data(type_req='products', sign=i_sig, index=index+1)
            process_and_save_products(res, index)
        except Exception as e:
            print(f"Ошибка при получении данных для продуктов c ключом {i_sig}: {e}")

def process_and_save_products(data: Dict[str, Any], index: Optional[int]) -> None:
    """
        Обрабатывает данные о товарах и сохраняет их в базу данных.

        Функция принимает объект данных с информацией о товарах, фильтрует товары, которые
        доступны для продажи (isAvailable=True), и сохраняет их в базу данных одним запросом.

        Аргументы:
        data (Dict[str, Any]): Объект, содержащий список товаров. Ожидается, что у каждого товара есть следующие атрибуты:
            - title (str): Название товара.
            - id (int): Уникальный идентификатор товара.
            - xml_id (int): Артикул товара.
            - brand_name (str): Название бренда.
            - webpage (str): URL страницы товара.
            - isAvailable (bool): Доступность товара (True, если товар доступен для продажи).
        index (Optional[int]): Индекс страницы или другого параметра, который может быть использован в дальнейшей логике.

        Операции:
        - Собирает данные о доступных товарах.
        - Массово вставляет собранные данные в таблицу `Products` с помощью Peewee.

        Возвращает:
        None
    """
    result = [] # Список для хранения информации о товарах
    data_art = [] # Список для хранения артикулов

    for value in data['data']['goods']:
        data_art.append(value['id'])
        data_art.append(value['id'])


        if len(value['packingVariants'])>1:
            for packingVariant in value['packingVariants']:
                arr = {
                    'title': value['title'],
                    'id': packingVariant['id'],
                    'xml_id': value['xml_id'],
                    'brand_name': value['brand_name'],
                    'url': value['webpage'],
                    'main_id': value['id'],
                    'isAvailable': value['isAvailable']
                }
                if packingVariant['id'] == value['id']:
                    arr['flag'] = 'main'
                else:
                    data_art.append(packingVariant['id'])
                result.append(arr)
        else:
            result.append({
                'title': value['title'],
                'id': value['id'],
                'xml_id': value['xml_id'],
                'brand_name': value['brand_name'],
                'url': value['webpage'],
                'flag': 'main',
                'main_id': value['id'],
                'isAvailable': value['isAvailable']
            })

    if result:
        Products.insert_many(result).execute()
        res = get_data_price(index, data_art) # Получаем цены для обновления
        calculate_price(res, data_art)  # Обновляем цены в базе данных


def calculate_price(data: Dict[str, Any], articles):
    """
        Функция для обновления цен, скидок и старых цен в базе данных продуктов.

        :param data: Словарь, содержащий данные о продуктах и их вариантах.
        :param articles: Список артикулов, которые будут использованы для обновления цен.
        """
    try:
        for value in data['data']['products']:
            if value['active_offer_id'] in articles:
                for offer in value['variants']:
                    Products.update(
                        price=offer['price']['actual'],
                        discount=offer['discount'],
                        old_price=offer['price']['old']
                    ).where(Products.main_id==offer['id']).execute()
    except Exception as e:
        print(f'Ошибка {e}')


def save_to_excel_chunk(products: List[dict], workbook) -> None:
    """
    Записывает данные о товарах в Excel-файл.

    Аргументы:
    - products (list): Список товаров для записи.
    - workbook: Объект рабочей книги Excel.
    """
    sheet = workbook.active

    for product in products:
        row = [
            product['xml_id'],
            product['title'],
            product['url'],
            product['price'],
            product['discount'],
            product['old_price']
        ]
        sheet.append(row)


def process_and_save_all_products(filename: str) -> None:
    """
    Извлекает данные из базы данных по 30 записей и сохраняет их в Excel-файл.

    Аргументы:
    - filename (str): Имя файла Excel для сохранения.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Products"

    # Заголовки столбцов
    headers = ["id товара", "Наименование", "Ссылка", "Актуальная цена", "Скидка", "Цена без скидки"]
    sheet.append(headers)

    # Инициализация параметров для постраничного извлечения данных
    offset = 0
    chunk_size = 30

    while True:
        # Получаем следующую порцию товаров
        query = Products.select().offset(offset).limit(chunk_size)
        products_chunk = list(query.dicts())

        if not products_chunk:
            break  # Если больше нет данных, выходим из цикла

        # Записываем текущий чанк в Excel
        save_to_excel_chunk(products_chunk, workbook)

        # Переходим к следующей порции данных
        offset += chunk_size

    # Сохраняем файл Excel
    workbook.save(filename)
    print(f"Все данные сохранены в файл: {filename}")

