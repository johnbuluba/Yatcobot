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
        mutations.append(' {} '.format(keyword))
        mutations.append('{} '.format(keyword))
        mutations.append(' {}'.format(keyword))
        mutations.append('#{}'.format(keyword))
        mutations.append(',{}'.format(keyword))
        mutations.append('{},'.format(keyword))
        mutations.append('.{}'.format(keyword))
        mutations.append('{}.'.format(keyword))
        mutations.append('{}!'.format(keyword))
        mutations.append('!{}'.format(keyword))
    return mutations
