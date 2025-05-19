import rasterio
from rasterio.merge import merge
import glob
import os

def merge_geotiffs(input_files, output_file):
    #Объединние нескольких GeoTIFF-файлов в один

    # Открываем все исходные файлы
    src_files_to_mosaic = []
    for file in input_files:
        src = rasterio.open(file)
        src_files_to_mosaic.append(src)

    # Объединяем файлы
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Копируем метаданные из первого файла
    out_meta = src.meta.copy()

    # Обновляем метаданные для объединенного файла
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "count": mosaic.shape[0]  # Количество каналов
    })

    # Сохраняем объединенный файл
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Закрываем все исходные файлы
    for src in src_files_to_mosaic:
        src.close()

    print(f"Объединенный файл сохранен как: {output_file}")

if __name__ == "__main__":
    # Получаем список всех GeoTIFF-файлов в папке photos_geotiff
    input_files = glob.glob(os.path.join('photos_geotiff', '*.tif'))

    if not input_files:
        print("Не найдены GeoTIFF-файлы в папке 'photos_geotiff'")
    else:
        # Сохраняем на уровень выше (в родительскую директорию)
        output_file = os.path.join('merged_output.tif')

        # Получаем абсолютный путь для наглядности
        abs_output_path = os.path.abspath(output_file)

        merge_geotiffs(input_files, output_file)
        print(f"Объединенный файл сохранен как: {abs_output_path}")