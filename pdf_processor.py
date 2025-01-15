# Для считывания PDF

# Для удаления дополнительно созданных файлов
import typing
from pathlib import Path

import PyPDF2
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для выполнения OCR, чтобы извлекать тексты из изображений
import pytesseract
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure, LTTextBoxHorizontal

pdf_path = 'test_task.pdf'


class PDFProcessor:

    def __init__(
            self,
            path_to_pdf: Path | str
    ):
        self.pdf_file = path_to_pdf

    def __enter__(self):
        # создаём объект файла PDF
        self.pdf_file_obj = open(self.pdf_file, 'rb')

        # создаём объект считывателя PDF
        self.pdf_readed = PyPDF2.PdfReader(self.pdf_file_obj)
        return self

    def __exit__(
            self,
            exc_type,
            exc_val,
            exc_tb
    ):
        self.pdf_file_obj.close()

    @staticmethod
    def get_line_text(
            element: LTTextBoxHorizontal
    ) -> str:
        """
        Распознает текст элемента.
        :param element: Элемент, текст которого необходимо распознать.
        :return: Текст элемента.
        """
        return element.get_text()

    def pdf_text_extraction(
            self,
            element: LTTextContainer
    ) -> tuple[str, list[str]]:
        """
        Парсит текст элемента.
        :param element: Элемент файла.
        :return: Кортеж, содержащий текст каждой строки и его формат.
        """

        # Инициализируем список со всеми форматами, встречающимися в строке текста
        line_formats = []

        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Итеративно обходим каждый символ в строке текста
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Добавляем к символу название шрифта
                        line_formats.append(character.fontname)
                        # Добавляем к символу размер шрифта
                        line_formats.append(character.size)
        # Находим уникальные размеры и названия шрифтов в строке
        format_per_line = list(set(line_formats))

        # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
        return self.get_line_text(element), format_per_line

    @staticmethod
    def crop_image(element: LTFigure, pageObj):
        # Получаем координаты для вырезания изображения из PDF
        [image_left, image_top, image_right, image_bottom] = [element.x0, element.y0, element.x1, element.y1]

        # Обрезаем страницу по координатам (left, bottom, right, top)
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)

        # Сохраняем обрезанную страницу в новый PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(pageObj)

        # Сохраняем обрезанный PDF в новый файл
        with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

    @staticmethod
    def convert_to_images(
            input_file_path: Path | str
    ) -> None:
        """
        Преобразует PDF в png изображение.
        :param input_file_path: путь к PDF файлу.
        :return: None
        """
        images = convert_from_path(input_file_path)
        image = images[0]
        output_file = "PDF_image.png"
        image.save(output_file, "PNG")

    @staticmethod
    def image_to_text(
            image_path
    ) -> str:
        """
        Считывает текст из изображения.
        :param image_path:
        :return:
        """
        # Считываем изображение
        img = Image.open(image_path)

        # Извлекаем текст из изображения
        text = pytesseract.image_to_string(img)
        return text

    # Извлечение таблиц из страницы
    @staticmethod
    def extract_table(
            pdf_path: Path | str,
            page_num: int,
            table_num: int
    ) -> list[list[str | None]]:
        """
        Извлекает таблицы из страницы.
        :param pdf_path: Путь к PDF файлу.
        :param page_num: Номер страницы.
        :param table_num: Номер таблицы.
        :return: Таблицу со страницы.
        """
        # Открываем файл pdf
        pdf = pdfplumber.open(pdf_path)

        # Находим исследуемую страницу
        table_page = pdf.pages[page_num]

        # Извлекаем соответствующую таблицу
        table = table_page.extract_tables()[table_num]
        return table

    # Преобразуем таблицу в соответствующий формат
    @staticmethod
    def table_converter(table: typing.Sized) -> str:
        """
        Преобразует таблицу в читаемый формат.
        :param table: Таблица
        :return: Данные из таблицы в виде строки
        """
        table_string = ''
        # Итеративно обходим каждую строку в таблице
        for row_num in range(len(table)):
            row = table[row_num]
            # Удаляем разрыв строки из текста с переносом
            cleaned_row = [
                item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for
                item
                in row]
            # Преобразуем таблицу в строку
            table_string += ('|' + '|'.join(cleaned_row) + '|' + '\n')
        # Удаляем последний разрыв строки
        table_string = table_string[:-1]
        return table_string

    def process_pdf(self):
        """
        Итеративно обрабатывает PDF файл.
        Разбирает текст и таблицы.
        :return: Обработанные данные со страницы.
        """
        text_per_page = {}

        page_text = []
        line_format = []
        text_from_tables = []
        page_content = []
        # Инициализируем количество исследованных таблиц

        table_num = 0
        first_element = True
        table_extraction_flag = False

        for pagenum, page in enumerate(extract_pages(pdf_path)):
            pdf = pdfplumber.open(pdf_path)
            # Находим исследуемую страницу
            page_tables = pdf.pages[pagenum]
            # Находим количество таблиц на странице
            tables = page_tables.find_tables()

            # Находим все элементы
            page_elements = [(element.y1, element) for element in page._objs]

            # Сортируем все элементы по порядку нахождения на странице
            page_elements.sort(key=lambda a: a[0], reverse=True)

            # Находим элементы, составляющие страницу
            for i, component in enumerate(page_elements):
                # Извлекаем положение верхнего края элемента в PDF
                print(component)
                pos = component[0]

                # Извлекаем элемент структуры страницы
                element = component[1]

                # Проверяем, является ли элемент текстовым
                if isinstance(element, LTTextContainer):
                    # Проверяем, находится ли текст в таблице
                    if not table_extraction_flag:
                        # Используем функцию извлечения текста и формата для каждого текстового элемента
                        (line_text, format_per_line) = self.pdf_text_extraction(element)
                        # Добавляем текст каждой строки к тексту страницы
                        page_text.append(line_text.rstrip())
                        # Добавляем формат каждой строки, содержащей текст
                        line_format.append(format_per_line)
                        page_content.append(
                            {"line_text": line_text.rstrip(), "pos": pos, "line_format": format_per_line})
                    else:
                        # Пропускаем текст, находящийся в таблице
                        pass

                # Проверяем элементы на наличие изображений
                if isinstance(element, LTFigure):
                    raise Exception("В файле найдены изображения, что не соответствует эталону.")

                # Проверяем элементы на наличие таблиц
                if isinstance(element, LTRect):
                    # Если первый прямоугольный элемент
                    if first_element == True and (table_num + 1) <= len(tables):
                        # Находим ограничивающий прямоугольник таблицы
                        lower_side = page.bbox[3] - tables[table_num].bbox[3]
                        upper_side = element.y1
                        # Извлекаем информацию из таблицы
                        table = self.extract_table(pdf_path, pagenum, table_num)
                        # Преобразуем информацию таблицы в формат структурированной строки
                        table_string = self.table_converter(table)
                        # Добавляем строку таблицы в список
                        text_from_tables.append({"table_text": table_string, "pos": pos, "lower_side": lower_side})
                        page_content.append({"page_content": table_string, "pos": pos, "upper_side": upper_side})
                        # Устанавливаем флаг True, чтобы избежать повторения содержимого
                        table_extraction_flag = True
                        # Преобразуем в другой элемент
                        first_element = False
                        # Добавляем условное обозначение в списки текста и формата
                        page_text.append('table')
                        line_format.append('table')

                        # # Проверяем, извлекли ли мы уже таблицы из этой страницы
                        if element.y0 >= lower_side and element.y1 <= upper_side:
                            pass
                        elif not isinstance(page_elements[i + 1][1], LTRect):
                            table_extraction_flag = False
                            first_element = True
                            table_num += 1

            # Создаём ключ для словаря
            dctkey = 'Page_' + str(pagenum)
            # Добавляем список списков как значение ключа страницы
            text_per_page[dctkey] = [page_content, text_from_tables]

        return text_per_page


def parse_pdf(pdf_path: Path | str):
    with PDFProcessor(pdf_path) as processor:
        return processor.process_pdf()['Page_0'][0]

# Сравнение эталонного файла с другим PDF файлом происходит следующим образом:
# Текст элементов роли не играет, проверяется их положение на странице, шрифты и прочее.
def compare_pdf(pdf_path: Path | str):
    """
    Сравнивает расположение элементов на странице и их шрифты с эталонным файлом.
    :param pdf_path:
    :return:
    """
    reference_pdf_path = 'test_task.pdf'
    reference_pdf = parse_pdf(reference_pdf_path)

    new_pdf = parse_pdf(pdf_path)

    desired_keys = ["pos", "line_format"]

    ref_filtered_data = [{k: d[k] for k in desired_keys if k in d} for d in reference_pdf]
    new_filtered_data = [{k: d[k] for k in desired_keys if k in d} for d in new_pdf]

    assert ref_filtered_data == new_filtered_data, f"Расположение и формат элементов не соответствует эталону"
