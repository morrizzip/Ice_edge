# Ice Edge Detection

## Описание проекта
Данный проект представляет собой программное обеспечение для автоматизированного анализа спутниковых снимков ледового покрова, выделения границы льда и публикации полученной информации на геоинформационном портале университета МАУ. Проект использует данные со спутников, предоставляемые сервисом ВЕГА-Science, и реализует алгоритмы обработки изображений для автоматического определения кромки льда.

## Функциональность
Программа обеспечивает следующий функционал:
*   Автоматизированная загрузка спутниковых снимков с сервиса ВЕГА-Science.
*   Геопривязка спутниковых снимков.
*   Объединение нескольких снимков в одно мозаичное изображение.
*   Удаление участков суши с изображения.
*   Автоматическое определение границы льда на изображении.
*   Расчет географических координат границы льда.
*   Публикация координат границы льда на геоинформационном портале университета для визуализации на карте.

## Технологии
В проекте используются следующие технологии:
*   **Python:** Основной язык программирования.
*   **PyCharm:** Интегрированная среда разработки.
*   **Requests:** Библиотека Python для работы с API ВЕГА-Science.
*   **QGIS:** Геоинформационная система (используется для ручной геопривязки).
*   **OpenCV:** для работы с алгоритмами компьютерного зрения;
*   **Matplotlib:** для визуализации данных, полученных со снимков;
*   **GDAL:** для чтения и записи растровых форматов геопространственных данных;
*   **Requests:** для составления HTTP-запросов;
*   **Pyproj:** для выполнения картографических преобразований между разными системами координат.

## Установка
1.  **Клонируйте репозиторий:**
    ```bash
    git clone [URL репозитория]
    cd [папка_репозитория]
    ```
2.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt 
    ```

## Алгоритм работы пользователя
1.  **Автоматическая загрузка снимков:** Программный модуль `DownloadPhotos.py` автоматически запускается в операционной системе Linux (рекомендуется использовать cron) раз в конце месяца с января по март и скачивает с сервиса ВЕГА-Science снимки со спутников в папку `photos`.
2.  **Ручная геопривязка:** Пользователю необходимо открыть полученные снимки в программе QGIS, назначить им координаты и сохранить полученные изображения в формате .tiff в папку `photos_geotiff`, расположенную в одной директории со всеми программными модулями проекта.
3.  **Объединение изображений:** Запустите программный модуль `CombinePhotos.py`, который объединяет полученные изображения из папки `photos_geotiff` в одно изображение.
4.  **Удаление суши:** Запустите модуль `CoordsWithoutEarth.py`, который удаляет из полученного изображения части, относящиеся к суше, и сохраняет полученный результат в директории со всеми модулями проекта.
5.  **Определение границ льда:** Запустите модуль `GetCoords.py`, в котором происходит определение координат границ льда.
6.  **Публикация на геопортале:** Запустите модуль `Adding_ice_data.py`, который полученные координаты передает на сервер геоинформационного портала университета для отображения их в виде полигонов на карте.

## Авторы
*   Баскова Вероника Кирилловна
*   Ефимова Злата Константиновна
*   Кошкина Варвара Геннадьевна
*   Краевая Анастасия Алексеевна
*   Лебедева Дарья Дмитриевна
*   Серопян Гнел Артурович
*   Ткачук Алина Викторовна

