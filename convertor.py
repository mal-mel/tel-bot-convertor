import requests
import datetime
from decimal import Decimal
from bs4 import BeautifulSoup


def date_today():
    today = str(datetime.datetime.now()).split()[:1]
    today = reversed(today[0].split('-'))
    today = ('/').join(today)
    return today


def get_quotes():
    date_req = f'date_req={date_today()}'
    cbr_xml = BeautifulSoup(requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?{date_req}').content, 'xml')
    return cbr_xml


def convert(amount, cur_from, cur_to):
    xml = get_quotes()

    if cur_from == '000':
        currency_from_rub = Decimal(amount)
        result = currency_from_rub / (
                    Decimal(xml.find('NumCode', text=cur_to).find_next_sibling('Value').string.replace(',', '.')) /
                    Decimal(xml.find('NumCode', text=cur_to).find_next_sibling('Nominal').string))

    elif cur_to == '000':
        result = \
            Decimal(xml.find('NumCode', text=cur_from).find_next_sibling('Value').string.replace(',', '.')) \
            / Decimal(xml.find('NumCode', text=cur_from).find_next_sibling('Nominal').string) * amount

    else:
        currency_from_rub = \
            Decimal(xml.find('NumCode', text=cur_from).find_next_sibling('Value').string.replace(',', '.')) \
            / Decimal(xml.find('NumCode', text=cur_from).find_next_sibling('Nominal').string) * amount

        result = Decimal(currency_from_rub) \
            / (Decimal(xml.find('NumCode', text=cur_to).find_next_sibling('Value').string.replace(',', '.')) /
               Decimal(xml.find('NumCode', text=cur_to).find_next_sibling('Nominal').string))

    return result.quantize(Decimal('1.00'))
