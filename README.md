# erp.aero
Содержит вариант решения задач №1 и №2.

## Подготовка
- скачать и установить Python 3 
- клонировать проект
- создать виртуальное окружение в папке проекта (После активации виртуального окружения, все пакеты Python будут устанавливаться и храниться только в этом окружении, изолированном от других проектов и системных установок Python.)
    Для Windows 
        установка - `pip install virtualenv`
        создание -   `python -m venv venv`
        активация - `.\venv\Scripts\activate`

    MacOS & Linux -
        установка - `pip install virtualenv`
        создание -   `virtualenv venv`
        активация - `./venv/bin/activate`
- 
## Примечание 
    Если у вас уже было установлено вирутальное окружение и/или что-то пошло не так
- удаление всех пакетов:
    Выполните следующие команды в терминале (Command Prompt) 
        `pip freeze`
        `pip freeze | xargs pip uninstall -y`
Эта команда сначала получает список всех установленных пакетов с помощью pip freeze, а затем передает каждый пакет в pip uninstall -y, чтобы удалить его.

## Проверка 
- выполнить команду `pip install -r requirements.txt` в корне локального репозитория для установки всех модулей


