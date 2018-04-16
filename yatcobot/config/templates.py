import confuse


class NumberKeywordsTemplate(confuse.Template):
    """
    Config template that has numbers as keys and keywords as values
    for example
      1: ['keyword1', 'keyword2']
      2: 'keyword1'

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def value(self, view, template=None):
        out = confuse.AttrDict()

        for key, value in view.items():
            if not isinstance(key, int):
                self.fail('Number keywords must have integer keys', view, type_error=True)
            out[key] = value.as_str_seq()

        return out

    def __repr__(self):
        return 'NumberKeywordsTemplate()'
