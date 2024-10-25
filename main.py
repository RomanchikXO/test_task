from DataBase.db import create_tables
from core.data_processing import all_data_get, process_and_save_all_products

if __name__ == "__main__":
    create_tables()
    all_data_get()
    process_and_save_all_products("products.xlsx")