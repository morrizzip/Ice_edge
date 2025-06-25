import numpy as np
import cv2
import matplotlib.pyplot as plt
from osgeo import gdal, osr

def load_sar_image(file_path):
    dataset = gdal.Open(file_path)
    band = dataset.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr.astype(np.float32), dataset


def preprocess_image(img):
    # 1. Логарифмирование с защитой от выбросов
    img_log = np.log1p(np.clip(img, 0, np.percentile(img, 99)))

    # 2. Более мягкая нормализация
    img_norm = cv2.normalize(img_log, None, 0, 255, cv2.NORM_MINMAX)

    # 3. Умеренное CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_enhanced = clahe.apply(img_norm.astype(np.uint8))

    return img_enhanced


def segment_ice_water_land(img):
    """
    Сегментация изображения:
    - Лед: самые светлые области (255)
    - Вода: черные, темно-серые и серые области (0)
    - Земля: все остальное (128)
    """
    # Нормализация с расширенным диапазоном
    img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Адаптивная бинаризация для лучшего выделения темных областей
    img_blur = cv2.medianBlur(img_norm, 7)
    thresh = cv2.adaptiveThreshold(img_blur, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 21, 7)

    # Определение порогов
    water_mask = (img_blur < np.percentile(img_blur, 65)).astype(np.uint8) * 255
    ice_mask = (img_blur > np.percentile(img_blur, 93)).astype(np.uint8) * 255

    segmented = np.zeros_like(img_blur)

    # Вода (черные, темные и серые области)
    segmented[water_mask == 255] = 0

    # Лед (только самые яркие области)
    segmented[ice_mask == 255] = 255

    # Все остальное - земля
    segmented[(water_mask == 0) & (ice_mask == 0)] = 128

    # Улучшенная морфологическая обработка
    kernel = np.ones((7, 7), np.uint8)
    segmented = cv2.morphologyEx(segmented, cv2.MORPH_CLOSE, kernel, iterations=1)
    segmented = cv2.morphologyEx(segmented, cv2.MORPH_OPEN, kernel, iterations=1)

    return segmented


def detect_ice_water_edge(segmented, original_img):
    # Создаем маску льда (белые области)
    ice_mask = (segmented == 255).astype(np.uint8) * 255

    # Находим границы с помощью детектора Канни
    edges = cv2.Canny(ice_mask, 50, 150)

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Фильтрация по площади
    min_contour_area = 100
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

    return contours


def get_geo_coordinates(contours, dataset):
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    source_srs = osr.SpatialReference()
    source_srs.ImportFromWkt(projection)
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source_srs, target_srs)

    contours_coords = []
    for contour in contours:
        contour_coords = []
        for point in contour.squeeze():
            x = geotransform[0] + point[0] * geotransform[1] + point[1] * geotransform[2]
            y = geotransform[3] + point[0] * geotransform[4] + point[1] * geotransform[5]
            lon, lat, _ = transform.TransformPoint(x, y)
            contour_coords.append((lon, lat))
        contours_coords.append(contour_coords)

    return contours_coords


def visualize_all_steps(original, processed, segmented, contours):
    plt.figure(figsize=(18, 12))

    plt.subplot(2, 2, 1)
    plt.imshow(original, cmap='gray')
    plt.title('1. Оригинальное изображение')

    plt.subplot(2, 2, 2)
    plt.imshow(processed, cmap='gray')
    plt.title('2. После обработки')

    plt.subplot(2, 2, 3)
    plt.imshow(segmented, cmap='gray')
    plt.title('3. Сегментация (вода-лед-земля)')

    result = cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(result, contours, -1, (255, 0, 0), 2)

    plt.subplot(2, 2, 4)
    plt.imshow(result)
    plt.title('4. Граница льда (красная)')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    img_path = '/home/student/Ice_edge/output_masked.tif'

    try:
        # Загрузка изображения
        img, dataset = load_sar_image(img_path)
        original = img.copy()

        # Предварительная обработка
        processed = preprocess_image(img)

        # Сегментация (светлые = лед, темные = вода)
        segmented = segment_ice_water_land(processed)

        # Детекция границ
        contours = detect_ice_water_edge(segmented, processed)

        # Получение географических координат
        geo_coords = get_geo_coordinates(contours, dataset)

        # Визуализация
        visualize_all_steps(original, processed, segmented, contours)

        # Вывод и сохранение координат
        print("\nГеографические координаты границы льда (долгота, широта):")
        for i, contour_coords in enumerate(geo_coords):
            if i > 0:
                print()
            print(f"Контур #{i + 1}:")
            for j, (lon, lat) in enumerate(contour_coords[:50], 1):
                print(f"{j}. {lon:.6f}, {lat:.6f}")

        with open(f'ice_edge_coordinates.txt', 'w') as f:
            for i, contour_coords in enumerate(geo_coords):
                if i > 0:
                    f.write("\n")
                for lon, lat in contour_coords:
                    f.write(f"{lon:.6f}, {lat:.6f}\n")
            print(f'Координаты сохранены в файл ice_edge_coordinates.txt')

    except Exception as e:
        print(f"Ошибка: {str(e)}")
