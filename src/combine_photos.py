import rasterio
from rasterio.merge import merge
import glob
import os

def merge_geotiffs(input_files, output_file):
    # Объединение нескольких GeoTIFF-файлов в один

    src_files_to_mosaic = []
    for file in input_files:
        src = rasterio.open(file)
        src_files_to_mosaic.append(src)

    mosaic, out_trans = merge(src_files_to_mosaic)

    # Копирование метаданных из первого файла
    out_meta = src.meta.copy()

    # Обновление метаданных для объединенного файла
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "count": mosaic.shape[0]  # Количество каналов
    })

    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(mosaic)

    for src in src_files_to_mosaic:
        src.close()

    print(f"Объединенный файл сохранен как: {output_file}")

if __name__ == "__main__":

    input_files = glob.glob(os.path.join('data/photos_geotiff', '*.tif'))

    if not input_files:
        print("Не найдены GeoTIFF-файлы в папке 'data/photos_geotiff'")
    else:
        output_dir = 'data'

        output_file = os.path.join(output_dir, 'merged_output.tif')

        abs_output_path = os.path.abspath(output_file)
        merge_geotiffs(input_files, output_file)
        print(f"Объединенный файл сохранен как: {output_file}")
