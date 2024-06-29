# Анализатор страниц

[Приложение](https://python-project-83-production-1fe4.up.railway.app) анализирует веб-страницы на их SEO-пригодность по аналогии с [PageSpeed Insights](https://pagespeed.web.dev/).

## Как работать с анализатором

Необходимо:

1. [Добавить сайт](https://youtu.be/o22e3yJ-9tY)
2. [Выполнить проверку сайта](https://youtu.be/02SaGKLPAPo)

## Запуск анализатора в локальной среде

Необходимо:

1. Установить:
   - Python версии, совместимой с 3.8
   - Poetry
   - Flask
   - Postgre SQL
2. Выполнить скрипт `database.sql` в выделенной для проекта БД
3. Поместить в корень проекта текстовый файл .env, содержащий следующие строки:
   - SECRET_KEY = "Произвольное значение"
   - DATABASE_URL = "URL выделенной БД"
3. Выполнить команду `poetry install` в корне проекта
4. Запустить веб сервер командой `flask --app путь-к-директории-проекта/page_analyzer/app run --port 8000`

## Статус непрерывной интеграции

[![Actions Status](https://github.com/RKV102/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/RKV102/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/5f8dbe355e6c453f8f5c/maintainability)](https://codeclimate.com/github/RKV102/python-project-83/maintainability)