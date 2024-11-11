#!/usr/bin/python

import json
import re
import argparse
import sys
import zipfile
import io
import os
from urllib.request import urlopen

# Константы для базовых URL-адресов
URL = "https://github.com"
APIURL = "https://api.github.com/repos"
RAWURL = "https://raw.githubusercontent.com"
ICON_DIR = "icons"  # Папка для сохранения иконок

# Создаем папку для иконок, если она не существует
if not os.path.exists(ICON_DIR):
    os.makedirs(ICON_DIR)

##
#  Функция для получения SHA коммита из ветки `master` репозитория на GitHub.
#
#  repo_path - Путь к репозиторию в формате "/owner/repo_name"
#  Возвращает: SHA коммита ветки `master`, если успешно, или False в случае ошибки.
#
def getSha(repo_path):
    url = APIURL + repo_path + "/branches/master"

    try:
        # Для Python 3
        if sys.version_info >= (3, 0):
            content = urlopen(url)  # Выполняем запрос
            data = content.read()  # Читаем данные
            encoding = content.info().get_content_charset('utf-8')  # Определяем кодировку
            JSON_object = json.loads(data.decode(encoding))  # Декодируем данные в JSON
            return JSON_object['commit']['sha']  # Возвращаем SHA коммита
        else:
            # Для Python 2
            data = json.load(urlopen(url))  # Декодируем данные в JSON
            return data['commit']['sha']  # Возвращаем SHA коммита

    except Exception as e:
        print(f"Error getting SHA for {repo_path}: {e}")
        return False


##
#  Функция для извлечения пути к репозиторию из URL.
#
#  url - полный URL репозитория
#  Возвращает: путь к репозиторию без префикса "https://github.com".
#
def repoPath(url):
    return url.replace(URL, '').replace('\n', '').replace('\r', '')  # Очищаем от ненужных символов


##
#  Функция для получения содержимого файла `plugin.json` из репозитория.
#
#  repo_path - Путь к репозиторию в формате "/owner/repo_name"
#  sha - SHA коммита, для которого нужно получить файл `plugin.json`
#  Возвращает: Содержимое файла `plugin.json` в виде Python словаря, или False в случае ошибки.
#
def getPluginJson(repo_path, sha):
    url = RAWURL + repo_path + "/" + sha + "/plugin.json"  # Формируем URL для получения plugin.json

    try:
        # Для Python 3
        if sys.version_info >= (3, 0):
            content = urlopen(url)  # Выполняем запрос
            data = content.read()  # Читаем данные
            encoding = content.info().get_content_charset('utf-8')  # Определяем кодировку
            JSON_object = json.loads(data.decode(encoding))  # Декодируем данные в JSON
            return JSON_object  # Возвращаем содержимое plugin.json
        else:
            # Для Python 2
            data = json.load(urlopen(url))  # Декодируем данные в JSON
            return data  # Возвращаем содержимое plugin.json
    except Exception as e:
        print(f"Error getting plugin.json for {repo_path} at {sha}: {e}")
        return False


##
#  Функция для получения URL иконки плагина.
#
#  repo_path - Путь к репозиторию в формате "/owner/repo_name"
#  sha - SHA коммита, для которого нужно получить иконку
#  icon_name - Имя файла иконки
#  Возвращает: URL иконки плагина в репозитории.
#
def getIcon(repo_path, sha, icon_name):
    return RAWURL + repo_path + "/" + sha + "/" + icon_name  # Формируем URL для получения иконки


##
#  Функция для обработки прямых ссылок на ZIP-файлы.
#
#  url - Прямая ссылка на ZIP-архив
#  Возвращает: Содержимое файла `plugin.json` из распакованного архива или False в случае ошибки.
#
def handleZipUrl(url):
    try:
        # Загружаем ZIP-файл
        print(f"Downloading ZIP file from {url}")
        response = urlopen(url)
        zip_content = io.BytesIO(response.read())  # Читаем содержимое архива в память

        # Открываем архив
        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
            # Проверяем, есть ли файл plugin.json в архиве
            if 'plugin.json' in zip_ref.namelist():
                with zip_ref.open('plugin.json') as file:
                    plugin_json = json.load(file)  # Читаем JSON
                    icon_name = plugin_json.get('icon', None)  # Получаем имя иконки, если оно есть

                    # Извлекаем иконку, если она присутствует
                    if icon_name and icon_name in zip_ref.namelist():
                        with zip_ref.open(icon_name) as icon_file:
                            icon_data = icon_file.read()
                            # Сохраняем иконку с новым именем, основанным на id
                            icon_id = plugin_json.get('id', 'unknown')
                            icon_path = os.path.join(ICON_DIR, f"{icon_id}.png")
                            with open(icon_path, 'wb') as icon_save_file:
                                icon_save_file.write(icon_data)
                            plugin_json['icon'] = icon_path  # Указываем путь к иконке

                    return plugin_json
            else:
                print("plugin.json not found in the ZIP file.")
                return False
    except Exception as e:
        print(f"Error handling ZIP file: {e}")
        return False


##
#  Функция для преобразования ссылки Google Drive в прямую ссылку для скачивания.
#
#  url - Ссылка на файл на Google Drive
#  Возвращает: Прямую ссылку для скачивания файла.
#
def handleGoogleDriveUrl(url):
    file_id_match = re.search(r"drive\.google\.com/.+?id=([a-zA-Z0-9_-]+)", url)
    if file_id_match:
        file_id = file_id_match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"
    else:
        print("Google Drive link is not in the expected format.")
        return None


##
#  Главная функция для обработки репозиториев и создания итогового JSON.
#
#  Считывает список репозиториев или ссылок на ZIP-файлы, извлекает данные для каждого плагина и сохраняет в файл.
#
def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputfile", help="name of file with a list of git repositories or zip links", default="repos.txt")
    parser.add_argument("-t", "--title", help="Title")
    parser.add_argument("-o", "--outputfile", help="Name of output file", default="repo.json")
    args = parser.parse_args()

    # Инициализируем результат с пустым списком плагинов
    res = {u"version": 1, u"plugins": []}

    # Если задан заголовок, добавляем его в результат
    if args.title:
        res[u"title"] = args.title

    print(f"Opening {args.inputfile}")
    with open(args.inputfile, "r") as file:  # Открываем файл с репозиториями или ссылками

        # Обрабатываем каждую строку (репозиторий или ссылка на ZIP)
        for line in file:
            line = line.strip()  # Убираем лишние пробелы и символы новой строки
            print(f"Processing {line}")

            # Если строка заканчивается на ".zip", то это прямая ссылка на ZIP-файл
            if line.lower().endswith(".zip"):
                print(f"Handling direct ZIP URL: {line}")
                plugin_json = handleZipUrl(line)  # Обрабатываем как прямой ZIP-файл
                download_url = line  # Для прямых ссылок на ZIP, скачиваем по этому URL
            elif "drive.google.com" in line.lower():
                # Если это ссылка на Google Drive, преобразуем ее
                print(f"Handling Google Drive URL: {line}")
                direct_url = handleGoogleDriveUrl(line)
                if direct_url:
                    plugin_json = handleZipUrl(direct_url)  # Обрабатываем как прямой ZIP-файл
                    download_url = direct_url  # Для Google Drive прямой линк на архив
                else:
                    print("Failed to handle Google Drive link.")
                    continue
            else:
                # Иначе это GitHub репозиторий, обрабатываем как репозиторий
                repo_path = repoPath(line)
                sha = getSha(repo_path)

                if sha == False:
                    print("Could not find plugin")
                    continue

                print("Getting plugin.json file")
                plugin_json = getPluginJson(repo_path, sha)

                print("Setting downloadUrl")
                download_url = URL + repo_path + "/archive/" + sha + ".zip"  # Ссылка для скачивания архива с GitHub
                icon_url = getIcon(repo_path, sha, plugin_json.get('icon', ''))  # URL для иконки

            if plugin_json:
                print("Setting downloadUrl")
                plugin_json['downloadURL'] = download_url  # Устанавливаем правильную ссылку для скачивания архива
                
                # Сохраняем иконку, если она есть
                if 'icon' in plugin_json:
                    print(f"Icon saved as {plugin_json['icon']}")

                res['plugins'].append(plugin_json)  # Добавляем данные плагина в результат
            else:
                print("Failed to retrieve plugin data.")

    # Записываем результат в файл
    print(f"Writing {args.outputfile}")
    with open(args.outputfile, "w") as write_file:
        json.dump(res, write_file, indent=4)  # Записываем JSON в файл с отступами

    print("Done")


# Стартуем выполнение программы
if __name__ == "__main__":
    main()
