import requests
from secret import *
from pyproj import Transformer

#создание группы ресурсов
def createResourceGroup(url,parentID,display_name,description):
    r= requests.post(
        url=url,
        json={
            "resource": {
                "cls":"resource_group",
                "parent":{"id":parentID},
                "display_name": display_name,
                "description": description,}
        },
        auth=AUTH
    )
    return r

#создание слоя
def createLayer(url:str,parentID:int,display_name:str,geometry_type:str,fields:list,srs:int=3857,description:str=''):
    r= requests.post(
        url=url,
        json={
            "resource": {
                "cls":"vector_layer",
                "parent":{"id":parentID},
                "display_name": display_name,
                "description": description,},
            "vector_layer":{
                "srs":{ "id": srs },
                "geometry_type": geometry_type,
                "fields": fields,
            }
        },
        auth=AUTH
    )
    return r

#свойства
def createFeature(url:str, layerID:int, geometry:dict, properties:dict):
    r = requests.post(
        url=url,
        json={
            "resource": {
                "layer": {"id": layerID},
                "geometry": geometry,
                "properties": properties
            }
        },
        auth=AUTH
    )
    return r

#разделение больших файлов
def split_coordinates_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    polygons = []
    current_polygon = []

    for line in lines:
        line = line.strip()

        if not line:
            if current_polygon:
                polygons.append(current_polygon)
                current_polygon = []
            continue

        current_polygon.append(line)

    if current_polygon:
        polygons.append(current_polygon)

    file_index = 0
    line_count = 0
    output_lines = []

    for polygon in polygons:
        output_lines.append('\n'.join(polygon))
        output_lines.append('')

        line_count += len(polygon) + 1

        # Если есть больше 1000 строк, сохраняем текущий набор в файл
        if line_count >= 1000:
            output_file_name = f'coordinate_part_{file_index}.txt'
            with open(output_file_name, 'w') as out_file:
                out_file.write('\n'.join(output_lines).strip())
            print(f"File created: {output_file_name}")

            line_count = 0
            output_lines = []
            file_index += 1

    # Сохраняем оставшиеся строки, если они есть
    if output_lines:
        output_file_name = f'coordinate_part_{file_index}.txt'
        with open(output_file_name, 'w') as out_file:
            out_file.write('\n'.join(output_lines).strip())
        print(f"File created: {output_file_name}")

    return file_index

#
#                 ДОБАВЛЕНИЕ ДАННЫХ
#

#преобразователь координат
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
#конвертор коориднат
def convert_coordinates(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    polygons = []
    current_polygon = []

    for line in lines:
        line = line.strip()

        if not line:
            if current_polygon:
                current_polygon.append(current_polygon[0])
                polygons.append(current_polygon)
                current_polygon = []
            continue

        # обработка
        try:
            lat, lon = map(float, line.split(","))
            x, y = transformer.transform(lon, lat)
            current_polygon.append(f"{x} {y}")
        except ValueError:
            print(f"Error: {line}")

    if current_polygon:
        current_polygon.append(current_polygon[0])
        polygons.append(current_polygon)

    #вывод
    formatted_output = ', '.join(f"(({', '.join(polygon)}))" for polygon in polygons)
    result = f"{formatted_output}" if formatted_output else ""

    return result

#добавление точки
def addPointToVectorLayer(url: str, layerID: int, coordinates: tuple):
    feature = {
        "geom": f"POINT ({coordinates[0]} {coordinates[1]})",
    }

    print("Sending feature:", feature)

    r = requests.post(
        url=f'{url}{layerID}/feature/',
        json=feature,
        auth=AUTH,
    )

    #отладка
    print("Response status code:", r.status_code)
    try:
        print("Response content:", r.json())
    except ValueError:
        print("Response content is not in JSON format:", r.text)

    return r

#добавление точки из файла
def addPointsFromFile(file_path: str, url: str, layerID: int):
    with open(file_path, 'r') as f:
        for line in f:
            #обрезка координат вида [x, y]
            coords = line.strip().strip('[]').split(',')
            if len(coords) == 2:
                try:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    #из EPSG:4326 в EPSG:3857
                    x, y = transformer.transform(lon, lat)

                    coordinates = (x, y)
                    response = addPointToVectorLayer(url, layerID, coordinates)
                    print(response)
                except ValueError:
                    print(f"Error: {line}")

#добавление мультиполигона
def addMultiPolygonToVectorLayer(url, layerID, polygons):
    feature = {
        "geom": f"MULTIPOLYGON ({polygons})"
    }

    print("Sending feature:", feature)

    r = requests.post(
        url=f'{url}{layerID}/feature/',
        json=feature,
        auth=AUTH,
        verify=False
    )

    #отладка
    print("Response status code:", r.status_code)
    try:
        print("Response content:", r.json())
    except ValueError:
        print("Response content is not in JSON format:", r.text)

    return r

#мультилинии
def addMLinesToVectorLayer(url, layerID, polygons):
    feature = {
        "geom": f"MULTILINESTRING {polygons}"
    }

    print("Sending feature:", feature)

    r = requests.post(
        url=f'{url}{layerID}/feature/',
        json=feature,
        auth=AUTH,
        verify=False
    )

    #отладка
    print("Response status code:", r.status_code)
    try:
        print("Response content:", r.json())
    except ValueError:
        print("Response content is not in JSON format:", r.text)

    return r




