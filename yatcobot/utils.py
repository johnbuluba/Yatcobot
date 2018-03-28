def create_keyword_mutations(keyword):
    """
    Given a keyword, create various mutations to be searched inside a post
    :param keyword: the base keyword of the mutations
    :return: list of mutation
    """
    mutations = list()
    keyword = keyword.strip()
    mutations.append(' {} '.format(keyword))
    mutations.append('{} '.format(keyword))
    mutations.append(' {}'.format(keyword))
    mutations.append('#{}'.format(keyword))
    mutations.append(',{}'.format(keyword))
    mutations.append('{},'.format(keyword))
    mutations.append('.{}'.format(keyword))
    mutations.append('{}.'.format(keyword))
    return mutations
