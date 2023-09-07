## Установка

1. Установить зависимости:

   ```bash
   pip install -r requirements.txt

2. Установить браузер Chromium, который будет использоваться Playwright.

   ```bash
   playwright install chromium

3. Делал как тесты, по этому запускается с помощью Pytest

   ```bash
   pytest -s -v .\test_page.py

Есть вариант запуска на selene, запуск будет на удаленной машине. Но по времени ппц долго, вторая таблица 5 часов парсилась локально.
Шаг 2 соответственно пропускаем

```bash
   pytest -s -v .\test_page_selene.py