import json
import os
import time
from datetime import date

from selene import query
from selene.support.conditions import have, be
from selene.support.shared import browser
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options


def parse(filename):
    table = {}
    upper_level = ''
    middle_level = ''
    active_row = '//div[contains(@class, "cell-selected")]/../div[contains(@class, "cell-interactive")]'
    clickable = '//div[contains(@class, "cell-selected")]/../div[1]/div[contains(@class, "clickable")]'

    def save_table_to_file(table, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(table, file, ensure_ascii=False, indent=4)

    def extract_data(active):
        return [' ' if item.get(query.text) == '\xa0' else item.get(query.text) for item in active[1:10]]

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

    browser.all('.expandableContent')[0].click()

    i = 0
    while True:
        time.sleep(0.2)

        if not browser.element(active_row).matching(be.visible):
            break

        if i % 15 == 0 and i > 0:
            for _ in range(20):
                ActionChains(browser.driver).send_keys(Keys.ARROW_DOWN).perform()
            for _ in range(20):
                ActionChains(browser.driver).send_keys(Keys.ARROW_UP).perform()
        time.sleep(0.1)
        i += 1

        active = browser.all(active_row)
        try:
            if len(browser.all(clickable)) > 1:
                upper_level = active[0].get(query.text)
                middle_level = 'Всего'
                course_level = 'Всего'
                add_course_data(table, active, upper_level, middle_level, course_level)
            elif len(browser.all(clickable)) == 1:
                middle_level = active[0].get(query.text)
                course_level = 'Всего'
                add_course_data(table, active, upper_level, middle_level, course_level)
            else:
                course_level = active[0].get(query.text)
                add_course_data(table, active, upper_level, middle_level, course_level)
        except:
            pass
            # print(f'строка {i}  {active}'

        ActionChains(browser.driver).send_keys(Keys.ARROW_DOWN).perform()
        time.sleep(0.2)
        ActionChains(browser.driver).send_keys(Keys.SPACE).perform()

    save_table_to_file(table, f'{filename}{date.today()}.json')

    return table


def next_page(clk: int = 1, hierarchy: int = 1):
    while clk > 0:
        browser.element('[aria-label="Next Page"]  i').click()
        # browser.element('[aria-label="Следующая страница"]  i').click()
        browser.element('.pivotTable').wait_until(be.visible)
        time.sleep(2)
        clk -= 1
    browser.all('.pivotTableCellWrap').by(have.text("Завершили обучение м1 офлайн")).first.hover()

    while hierarchy > 0:
        browser.element('[aria-label="Expand all down one level in the hierarchy"]').click()
        # browser.element('[aria-label="Развернуть все на один уровень вниз в иерархии"]').click()
        hierarchy -= 1


def clear_existing_file(*args):
    for item in args:
        if os.path.exists(item):
            os.remove(item)


def test_first():
    browser.element('.canvasFlexBox').wait_until(be.visible)
    next_page(1, 1)
    parse('first')


def test_second():
    next_page(2, 2)
    parse('second')


def test_third():
    next_page(3, 2)
    parse('third')
