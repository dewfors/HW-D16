import re
from django import template

register = template.Library()

FORBIDDEN_WORDS = ['допинг', 'треугольник']


def get_new_value(some_line):
    new_line = some_line
    forbidden_words = get_prepare_forbidden_words()
    words = get_words_for_check(some_line)

    words_to_replace = []
    for w in forbidden_words:
        if w[0] in words:
            words_to_replace.append(w)

    for w in words_to_replace:
        if w[0] in new_line:
            new_line = new_line.replace(w[0], w[1])

    return new_line


def get_words_for_check(some_line):
    words = []
    words_split = re.split(",|;| |!|-", some_line)
    for word in words_split:
        if word == '':
            continue
        if word not in words:
            words.append(word)

    return words


def get_prepare_forbidden_words():
    prepare_forbidden_words = []
    for word in FORBIDDEN_WORDS:
        replaced = word[0] + '*' * (len(word) - 1)
        prepare_forbidden_words.append((word, replaced))

        word_cap = word.capitalize()
        replaced = word_cap[0] + '*' * (len(word) - 1)
        prepare_forbidden_words.append((word_cap, replaced))

    return prepare_forbidden_words


@register.filter()
def censor(value):
    """
    Фильтр предназначен для замены букв нежелательных слов в заголовках и текстах статей на символ *
    value: значение, к которому нужно применить фильтр
    """
    new_line = get_new_value(value)

    return new_line
