from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField

db = SqliteDatabase("products.db")


class BaseModel(Model):
    class Meta:
        database = db


class Products(BaseModel):
    """
    Описание продукта

    Этот класс используется для хранения информации о продуктах в каталоге.
    Атрибуты:
    - title (str, optional): Название продукта.
    - url (str): URL продукта.
    - id (int, optional): Уникальный идентификатор продукта (числовой).
    - xml_id (int, optional): XML идентификатор продукта (числовой).
    - brand_name (str, optional): Название бренда продукта.
    - price (int, optional): Цена продукта в рублях (актуальная).
    - old_price (int, optional): цена без скидки если есть скидка.
    - discount (int, optional): Скидка на продукт в процентах.
    """

    title = CharField(null=True)
    url = CharField()
    id = IntegerField()
    xml_id = IntegerField(null=True)
    brand_name = CharField(null=True)
    price = IntegerField(null=True)
    old_price = IntegerField(null=True)
    discount = IntegerField(null=True)
    flag = CharField(null=True)
    main_id = IntegerField(null=True)
    isAvailable = BooleanField()


def create_tables():
    db.connect()
    db.create_tables([Products], safe=True)
