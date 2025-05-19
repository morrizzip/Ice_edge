import io
import os
import requests
from bs4 import BeautifulSoup
from vega import *

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
    for i, snapshot_id in enumerate(ids, start=1):
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


if __name__ == "__main__":
    # Параметры запроса
    BASE_URL = "http://sci-vega.ru/fap/toproxy"
    BBOX = "34.4794,63.747,44.8066,71.833"
    WIDTH = HEIGHT = 1240
    DATE = "2021-02-01"
    DATE_FROM = "2021-01-01"
    LIMIT = 150

    # Получаем параметры запроса
    metadata_url, metadata_params = get_all_params(
        base_url=BASE_URL,
        user=user,
        pwd=pwd,
        ukey=ukey,
        bbox=BBOX,
        width=WIDTH,
        height=HEIGHT,
        date=DATE,
        date_from=DATE_FROM,
        limit=LIMIT
    )

    # Отправляем запрос метаданных
    response = requests.get(metadata_url, params=metadata_params, auth=(user, pwd))
    data = response.json()

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

    print(f"Найдено снимков: {len(ids)}")
    print("IDs:", ids)
    print("Серверы:", servers)

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

    # Загружаем изображения
    download_images(
        base_url=BASE_URL,
        user=user,
        pwd=pwd,
        ukey=ukey,
        ids=ids,
        common_params=common_params,
        save_dir='photos'
    )