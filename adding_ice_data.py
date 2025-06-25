import adding_ice_data_api

base_url = 'https://geo.mauniver.ru/api/'
res_url = f'{base_url}resource/'

parentID = 218 #id родительской папки
pointID = 710 #id слоя для точек
mpID = 2067 #id слоя для мультиполигонов

# функция для получения ID слоя в зависимости от выбранной даты
def get_mpID_for_date(date):
    date_mpID_mapping = {
        "2020feb": 1951,
        "2021feb": 1961,
        "2022feb": 1962,
        "2020mar": 1963,
        "2021mar": 1964,
        "2022mar": 1965,
        "2020jan": 1966,
        "2021jan": 1967,
        "2022jan": 1968,
    }
    return date_mpID_mapping.get(date, None)

# ввод пользователя
selected_date = input("Выберите дату (формат YYYY или [YYYYmon]): ")

mpID = get_mpID_for_date(selected_date)

if mpID is not None:
    print(f"Выбранный ID слоя для мультиполигонов: {mpID}")
else:
    print("Неверная дата. Пожалуйста, выберите правильную дату.")

file_point = '.txt'  #координаты для точек
file_poly = 'ice_edge_coordinates.txt' #координаты для полигонов

# добавление мультиполигонов из больших файлов
k = adding_ice_data_api.split_coordinates_file(file_poly)

for i in range(k):
    file_path_poly = f'coordinate_part_{i}.txt'

    print(file_path_poly)

    result_coords = adding_ice_data_api.convert_coordinates(file_path_poly)
    print(result_coords)

    response = adding_ice_data_api.addMultiPolygonToVectorLayer(res_url, mpID, result_coords)
    print(f"Result: {file_path_poly}: {response}")



