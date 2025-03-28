import requests
from urllib.parse import urlparse, parse_qs


def extract_data_from_url(url):
    # Разбираем URL
    parsed_url = urlparse(url)
    # Извлекаем параметры запроса
    query_params = parse_qs(parsed_url.query)

    # Получаем нужные данные
    width = query_params.get('width', [''])[0]
    height = query_params.get('height', [''])[0]
    bbox = query_params.get('bbox', [''])[0]
    unisat_uids = query_params.get('unisat_uids', [''])[0]

    return {
        "WIDTH": width,
        "HEIGHT": height,
        "BBOX": bbox,
        "unisat_uids": unisat_uids
    }


def read_urls_from_file(file_path):
    # Читаем ссылки из текстового файла
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file.readlines()]  # Убираем лишние пробелы и переносы из каждой строки
    return urls


def fetch_and_save_image(params, image_file_name):
    url = "http://mau_api:DIg2e2+K@sci-vega.ru/fap/toproxy/export/local/smiswms/get_map.pl?ukey=53616c7465645f5f4d5d9043e4ef4a6f7c915d382c1a2260fd9f01800279786afb18a03f7be9b321"

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(f"Запрос выполнен успешно для {image_file_name}.")
        with open(image_file_name, "wb") as f:
            f.write(response.content)  # Сохраняем полученное изображение
    else:
        print(f"Ошибка при выполнении запроса для {image_file_name}: {response.status_code}")


# Пример использования
file_path = 'links.txt'
urls = read_urls_from_file(file_path)

for index, url in enumerate(urls):
    data = extract_data_from_url(url)

    params = {
        "layers": "unisat",
        "db_pkg_mode": "radarsat",
        "FORMAT": "png",
        "WIDTH": data["WIDTH"],
        "HEIGHT": data["HEIGHT"],
        "BBOX": data["BBOX"],
        "EXCEPTIONS": "xml",
        "SERVICE": "WMS",
        "REQUEST": "GetMap",
        "transparent": 1,
        "unisat_uids": data["unisat_uids"]
    }

    image_file_name = f"mapKolskiy{index + 1}.png"
    fetch_and_save_image(params, image_file_name)
