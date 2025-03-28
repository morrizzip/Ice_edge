import api
import coorconverter

base_url = 'https://geo.mauniver.ru/api/'
res_url = f'{base_url}resource/'
parentID = 218 #id родительской папки
pointID = 692 #id слоя для точек
polygonID = 481 #id слоя для полигонов
mpID = 668 #id слоя для мультиполигонов
n = 0 #количество нарезанных файлов

file_path = 'coordinates.txt'  #координаты для точек



#
# #                                   Создаём группу ресурсов и слои
#

# response = api.createResourceGroup(res_url,parentID,display_name="POINT",description='folder for point')
# print(response)

# response = api.createLayer(res_url,parentID,display_name='',description='',geometry_type="POINT",
#                               fields=[
#                                   {
#                                       "keyname": "",
#                                       "display_name": "",
#                                       "datatype": ""
#                                   },
#                                   {
#                                       "keyname": "",
#                                       "display_name": "",
#                                       "datatype": ""
#                                   },
#                               ]
#                               )
# print(response.status_code)
# print(response.json())




#
#                            добавление данных
#

# #точки
# response = api.addPointsFromFile(file_path, res_url, pointID)
# print(response)
#
#
# #добавление мультиполигонов из больших файлов
# for i in range(n + 1):
#     file_path_poly = f'coord1\polygon_part_{i}.txt'
#
#     print(file_path_poly)
#
#     result_coords = api.convert_coordinates(file_path_poly)
#     print(result_coords)
#
#     response = api.addMultiPolygonToVectorLayer(res_url, mpID, result_coords)
#     print(f"Result: {file_path_poly}: {response}")







