import io
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_date_input(prompt):
    """Функция для ввода даты с валидацией"""
    while True:
        date_str = input(prompt + " (гггг-мм-дд): ")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Неправильный формат даты. Пожалуйста, введите дату в формате гггг-мм-дд")


def get_all_params(base_url, user, pwd, ukey, bbox, width, height, date, date_from, limit=150):
    # URL для получения метаданных
    metadata_url = f"{base_url}/export/local/smiswms/get_metadata.pl?ukey={ukey}&REQUEST=GetMetadata"

    # Параметры запроса
    params = {
        "BBOX": bbox,
        "width": width,
        "height": height,
        "dt": date,
        "db_pkg_mode": "radarsat",
        "get_bbox": 1,
        "dt_from": date_from,
        "limit": limit,
        "layers": "unisat",
        "satellites": "SENTINEL-1A,SENTINEL-1B",
        "devices": "C_SAR_EW,C_SAR_IW",
        "products": "_radar_calib_vv,_radar_calib_vh,_radar_calib_hv,_radar_calib_hh,"
                    "_radar_hh,_radar_vv,_radar_hv,_radar_vh,"
                    "v_radar_simple_rgb,v_radar_calc_rgb,v_radar_nrvi_pal,"
                    "v_radar_nrvi_bw,v_radar_index,v_radar_index_inverse,"
                    "_radar_slc_vv,_radar_slc_hh,_radar_slc_hv,_radar_slc_vh",
        "srs": "smis:lonlat",
        "sid": "6dollm4qniprssf1",
        "default_products": "_radar_calib_vv,_radar_calib_vh,_radar_calib_hv,"
                            "_radar_calib_hh,_radar_hh,_radar_vv,_radar_hv,"
                            "_radar_vh,_radar_slc_vv,_radar_slc_vh,_radar_slc_hv,_radar_slc_hh"
    }

    return metadata_url, params


def download_images(base_url, user, pwd, ukey, ids, common_params, save_dir='photos', max_images=3):
    os.makedirs(save_dir, exist_ok=True)
    base_download_url = f"{base_url}/export/local/smiswms/get_map.pl?ukey={ukey}"
    print(f"Всего найдено снимков: {len(ids)}")

    for i, snapshot_id in enumerate(ids[:max_images], start=1):
        params = common_params.copy()
        params["unisat_uids"] = snapshot_id

        try:
            response = requests.get(base_download_url, params=params, auth=(user, pwd))
            response.raise_for_status()

            filename = os.path.join(save_dir, f"photo_{i}_{snapshot_id}.png")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Изображение сохранено как {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке изображения для ID {snapshot_id}: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка для ID {snapshot_id}: {e}")


def main():
    print("=== Программа загрузки спутниковых снимков ===")

    # Запрос дат у пользователя
    date_from = get_date_input("Введите начальную дату периода")
    date_to = get_date_input("Введите конечную дату периода")

    # Остальные параметры
    BASE_URL = "http://sci-vega.ru/fap/toproxy"
    BBOX = "34.4794,63.747,63.8525,71.7978"  # lon, lat
    WIDTH = HEIGHT = 1240
    LIMIT = 150

    # Получаем параметры запроса
    metadata_url, metadata_params = get_all_params(
        base_url=BASE_URL,
        user='mau_api',
        pwd='DIg2e2+K',
        ukey='53616c7465645f5f4d5d9043e4ef4a6f7c915d382c1a2260fd9f01800279786afb18a03f7be9b321',
        bbox=BBOX,
        width=WIDTH,
        height=HEIGHT,
        date=date_to,  # Используем введенную конечную дату
        date_from=date_from,  # Используем введенную начальную дату
        limit=LIMIT
    )

    # Отправляем запрос метаданных
    try:
        response = requests.get(metadata_url, params=metadata_params, auth=('mau_api', 'DIg2e2+K'))
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе метаданных: {e}")
        return
    except ValueError as e:
        print(f"Ошибка при разборе JSON ответа: {e}")
        return

    # Извлекаем IDs и серверы
    ids = []
    servers = []

    if 'DATA' in data:
        for item in data['DATA']:
            if 'products' in item:
                product_data = item['products']['default']
                if (snapshot_id := product_data.get("id")) and (snapshot_server := product_data.get("server")):
                    ids.append(snapshot_id)
                    servers.append(snapshot_server)

    print(f"\nНайдено снимков за период с {date_from} по {date_to}: {len(ids)}")
    if ids:
        print("Пример ID снимка:", ids[0])
        print("Пример сервера:", servers[0])

        # Общие параметры для загрузки изображений
        common_params = {
            "layers": "unisat",
            "db_pkg_mode": "radarsat",
            "FORMAT": "png",
            "WIDTH": WIDTH,
            "HEIGHT": HEIGHT,
            "BBOX": BBOX,
            "EXCEPTIONS": "xml",
            "SERVICE": "WMS",
            "REQUEST": "GetMap",
            "transparent": 1
        }

        # Запрашиваем количество снимков для загрузки
        while True:
            try:
                max_images = int(input(f"\nСколько снимков загрузить (доступно {len(ids)}, введите число): "))
                if 1 <= max_images <= len(ids):
                    break
                print(f"Пожалуйста, введите число от 1 до {len(ids)}")
            except ValueError:
                print("Пожалуйста, введите целое число")

        # Загружаем изображения
        download_images(
            base_url=BASE_URL,
            user='mau_api',
            pwd='DIg2e2+K',
            ukey='53616c7465645f5f4d5d9043e4ef4a6f7c915d382c1a2260fd9f01800279786afb18a03f7be9b321',
            ids=ids,
            common_params=common_params,
            save_dir='photos',
            max_images=max_images
        )
    else:
        print("Не найдено снимков для указанного периода.")


if __name__ == "__main__":
    main()
