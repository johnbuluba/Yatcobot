import re


def create_keyword_mutations(*keywords):
    """
    Given some keywords, create various mutations to be searched inside a post
    :param keywords: one or more keywords to be used
        as base of the mutations
    :return: list of mutation
    """
    mutations = list()

    for keyword in keywords:
        keyword = keyword.strip()
        keyword = keyword.lower()
        mutations.append(' {} '.format(keyword))
        mutations.append('#{} '.format(keyword))
        mutations.append(',{} '.format(keyword))
        mutations.append(' {},'.format(keyword))
        mutations.append('.{} '.format(keyword))
        mutations.append(' {}.'.format(keyword))
        mutations.append(' {}!'.format(keyword))
        mutations.append('!{} '.format(keyword))
    return mutations


def preprocess_text(text):
    text = text.replace('\n', ' ').replace('\r', '')
    text = text.lower()
    # Add space in both ends to make it easier to find words
    text = ' {} '.format(text)
    # Remove emoji
    # For more ranges see here https://www.unicode.org/emoji/charts/full-emoji-list.html
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U00002640-\U000027B0"  # dingbats
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)

    text = emoji_pattern.sub(r'', text)
    return text


def count_keyword_in_text(keyword, text):
    """
    Search how many times a keywords is found inside a string
    :param keyword: the keyword to search
    :param text: the text to be searchd
    :return: how many times the keyword is found
    """
    text.lower()
    text = ' ' + text.lower() + ' '
    return text.count(keyword)
