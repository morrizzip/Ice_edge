import adding_ice_data_api

base_url = 'https://geo.mauniver.ru/api/'
res_url = f'{base_url}resource/'

parentID = 218 #id родительской папки
pointID = 710 #id слоя для точек
mpID = 711 #id слоя для мультиполигонов
mlID = 712 #id для мультилиний



file_point = '.txt'  #координаты для точек
file_poly = 'ice_edge_coordinates.txt' #координаты для полигонов
file_line = 'ice_edge_coordinates.txt' #координаты для линий



#
# #                                   Создаём группу ресурсов и слои
#

# response = api.createResourceGroup(res_url,parentID,display_name="POINT",description='folder for point')
# print(response)

# response = api.createLayer(res_url,parentID,display_name='(release)',description='',geometry_type="",
#                               fields=[
#                                   {
#                                       "keyname": "name",
#                                       "display_name": "Name",
#                                       "datatype": "STRING",
#                                   },
#                                   {
#                                       "keyname": "description",
#                                       "display_name": "Description",
#                                       "datatype": "STRING",
#                                   },
#                               ]
#                               )
# print(response.status_code)
# print(response.json())




#
#                            добавление данных
#

# #точки
# response = api.addPointsFromFile(file_point, res_url, pointID)
# print(response)



# добавление мультиполигонов из больших файлов
k = adding_ice_data_api.split_coordinates_file(file_poly)

for i in range(k):
    file_path_poly = f'coordinate_part_{i}.txt'

    print(file_path_poly)

    result_coords = adding_ice_data_api.convert_coordinates(file_path_poly)
    print(result_coords)

    response = adding_ice_data_api.addMultiPolygonToVectorLayer(res_url, mpID, result_coords)
    print(f"Result: {file_path_poly}: {response}")



# # добавление мультилиний из больших файлов
# k = adding_ice_data_api.split_coordinates_file(file_line)
#
# for i in range(k):
#     file_path_line = f'coordinate_part_{i}.txt'
#
#     print(file_path_line)
#
#     result_coords = adding_ice_data_api.convert_coordinates(file_path_line)
#     print(result_coords)
#
#     response = adding_ice_data_api.addMLinesToVectorLayer(res_url, mlID, result_coords)
#     print(f"Result: {file_path_line}: {response}")



