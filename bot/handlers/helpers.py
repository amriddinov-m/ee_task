import datetime
import locale

locale.setlocale(locale.LC_NUMERIC, 'ru_RU.utf8')


def clear_int_string(int_string):
    """ Приводит значения вида ` 300 000` в `300000` """
    return int_string.strip().replace(' ', '')


def to_locale(value):
    return locale.format('%d', value, grouping=True)


def add_days_to_today(days):
    today = datetime.datetime.now().date()
    result_date = today + datetime.timedelta(days=int(days))
    return result_date


def file_processing(message):
    title = message.text
    file_id = ''
    file_type = ''
    if message.photo:
        file_id = message.photo[-1].file_id
        title = message.caption
        file_type = 'photo'
    elif message.document:
        file_id = message.document.file_id
        title = message.caption
        file_type = 'document'
    return {'title': title, 'file_id': file_id, 'file_type': file_type}