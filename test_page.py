import json
import os
import time
from datetime import date
from playwright.sync_api import sync_playwright, Page, Playwright, BrowserType


def extract_data(active):
    return [' ' if item.text_content() == '\xa0' else item.text_content() for item in active[1:10]]


def add_course_data(table, active, upper_level, middle_level, course_level):
    # Косяк может быть или в сортровке вложенных данных
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


def parse(page: Page, filename):
    table = {}
    upper_level = ''
    middle_level = ''
    active_row = '//div[contains(@class, "cell-selected")]/../div[contains(@class, "cell-interactive")]'
    clickable = '//div[contains(@class, "cell-selected")]/../div[1]/div[contains(@class, "clickable")]'

    page.locator('.expandableContent').all()[0].click()

    # Пытался отслеживать по активному классу, но почему то каждый раз где то в середине таблицы цикл вылетал.
    # Так и не понял почему, но если увеличивать таймауты выходит неприлично долгое выполнение.
    row = 0
    if filename == 'first':
        row = 203
    elif filename == 'second':
        row = 5491
    elif filename == 'third':
        row = 5428

    i = 0
    while True:
        if i > row:
            break

        # Из за того что не весь контент сразу появляется приходится крутить периодически, что бы кнопки раскрывания находились
        if i % 15 == 0 and 0 < i < row - 10:
            for _ in range(10):
                page.keyboard.press('ArrowDown')
            for _ in range(10):
                page.keyboard.press('ArrowUp')
        i += 1

        active = page.query_selector_all(active_row)

        # Или косяк где то тут, но тут как будто вряд ли.
        try:
            # Долго пытался понять как отделить вложенность друг от друга, ничего лучше чем искать кол-во вложенных кнопок расрывания (+) не смог придумать
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


def test_first_parse():
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

    context.close()
    browser.close()
    playwright.stop()


def test_second_parse():
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
        next_page(page, 2, 2)
        parse(page, 'second')
    except:
        print('second crush')

    context.close()
    browser.close()
    playwright.stop()


def test_third_parse():
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
        next_page(page, 3, 2)
        parse(page, 'third')
    except:
        print('third crush')

    context.close()
    browser.close()
    playwright.stop()
