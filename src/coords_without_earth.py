import json
import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid


def load_russia_boundary(gadm_file):
    # Загрузка и объединение всех полигонов России из GeoJSON
    with open(gadm_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    polygons = []
    for feature in data['features']:
        geom = make_valid(shape(feature['geometry']))
        if geom.geom_type == 'MultiPolygon':
            polygons.extend(geom.geoms)
        else:
            polygons.append(geom)

    return unary_union(polygons)


def mask_russia_from_tiff(input_tiff, output_tiff, russia_polygon):
    # Маска территории России в GeoTIFF файле
    with rasterio.open(input_tiff) as src:
        # Преобразование полигона в координаты CRS изображения
        russia_crs = russia_polygon.buffer(0)
        russia_geojson = [mapping(russia_crs)]

        # Инвертирование маски
        out_image, out_transform = mask(
            src,
            russia_geojson,
            crop=False,
            invert=True  # Исключение территории России
        )

        # Метаданные исходного файла
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "nodata": 0  # Значение для маскированных областей
        })

        with rasterio.open(output_tiff, "w", **out_meta) as dest:
            dest.write(out_image)


def main():

    gadm_file = "data/gadm.json"
    input_tiff = "data/merged_output.tif"
    output_tiff = "data/output_masked.tif"

    # Загрузка границ России
    russia = load_russia_boundary(gadm_file)

    # Применение маски
    mask_russia_from_tiff(input_tiff, output_tiff, russia)

    print(f"Обработка завершена. Результат сохранен в {output_tiff}")


if __name__ == "__main__":
    main()
