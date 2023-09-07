import json
import os
import time
from datetime import date
from playwright.sync_api import sync_playwright, Page, Playwright, BrowserType


def parse(page: Page, filename):
    table = {}
    upper_level = ''
    middle_level = ''
    active_row = '//div[contains(@class, "cell-selected")]/../div[contains(@class, "cell-interactive")]'
    clickable = '//div[contains(@class, "cell-selected")]/../div[1]/div[contains(@class, "clickable")]'

    def extract_data(active):
        return [' ' if item.text_content() == '\xa0' else item.text_content() for item in active[1:10]]

    def add_course_data(table, active, upper_level, middle_level, course_level):
        if upper_level not in table:
            table[upper_level] = {}

        if middle_level not in table[upper_level]:
            table[upper_level][middle_level] = {}

        if course_level not in table[upper_level][middle_level]:
            if middle_level == course_level:
                table[upper_level][course_level] = {}
            else:
                table[upper_level][middle_level][course_level] = []

        if middle_level == course_level:
            table[upper_level][course_level] = extract_data(active)
        else:
            table[upper_level][middle_level][course_level] = extract_data(active)

    page.locator('.expandableContent').all()[0].click()

    row = 0
    if filename == 'first':
        row = 203
    elif filename == 'second':
        row = 5491
    elif filename == 'third':
        row = 5428

    i = 0
    while True:
        time.sleep(0.2)
        if i > row:
            break

        if i % 15 == 0 and 0 < i < row - 10:
            for _ in range(10):
                page.keyboard.press('ArrowDown')
            for _ in range(10):
                page.keyboard.press('ArrowUp')
        i += 1

        active = page.query_selector_all(active_row)
        try:
            if len(page.locator(clickable).all()) > 1:
                upper_level = active[0].text_content()
                middle_level = 'Всего'
                course_level = 'Всего'
                add_course_data(table, active, upper_level, middle_level, course_level)
            elif len(page.locator(clickable).all()) == 1:
                middle_level = active[0].text_content()
                course_level = 'Всего'
                add_course_data(table, active, upper_level, middle_level, course_level)
            else:
                course_level = active[0].text_content()
                add_course_data(table, active, upper_level, middle_level, course_level)
        except:
            print(f'{filename} строка {i}  {active}')

        page.keyboard.press('ArrowDown')
        time.sleep(0.2)
        page.keyboard.press('Space')

    save_table_to_file(table, f'{filename}{date.today()}.json')
    return table


def save_table_to_file(table, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(table, file, ensure_ascii=False, indent=4)


def next_page(page: Page, click: int = 1, hierarchy: int = 1):
    while click > 0:
        page.locator('[aria-label="Следующая страница"]  i').click()
        page.locator('.pivotTable').wait_for(state='visible')
        click -= 1
    page.get_by_text("Завершили обучение м1 офлайн").hover()

    while hierarchy > 0:
        page.locator('[aria-label="Развернуть все на один уровень вниз в иерархии"]').click()
        hierarchy -= 1


def clear_existing_file(*args):
    for item in args:
        if os.path.exists(item):
            os.remove(item)


def test_parse():
    clear_existing_file('table.json')

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
    )
    context = browser.new_context(record_video_dir="videos/")
    page = context.new_page()

    page.goto(
        "https://app.powerbi.com/view?r=eyJrIjoiYzE1NGI1ZWItN2NhYi00MGJlLTllMGQtZDA0MTRhZTI3N2JjIiwidCI6IjhiYzM0YTk5LTYzMWMtNDhlMi04NjM4LTRiMzg0YmFmOTI3MCIsImMiOjl9")
    page.locator('.canvasFlexBox').wait_for(state='visible')

    try:
        next_page(page, 1, 1)
        parse(page, 'first')
    except:
        print('first crush')

    try:
        next_page(page, 1, 2)
        parse(page, 'second')
    except:
        print('second crush')

    try:
        next_page(page, 1, 2)
        parse(page, 'third')
    except:
        print('third crush')

    context.close()
    browser.close()
    playwright.stop()
