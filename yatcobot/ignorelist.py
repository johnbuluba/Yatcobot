class IgnoreList(set):
    """
    A list like object that loads contents from a file and everything that is appended here gets also
    appended in the file
    """

    def __init__(self, filename):
        self.filename = filename
        self.load_file()

    def append(self, p_object):
        """
        Adds an id to the ignore list and apeends it to the file
        :param p_object: int the id
        """
        if p_object not in self:
            self.append_file(p_object)
        super().add(p_object)

    def load_file(self):
        """
        loads an ignore list from a file
        """
        with open(self.filename, 'a+') as f:
            f.seek(0)
            self.update(int(x) for x in f.read().splitlines())

    def append_file(self, p_object):
        """
        append an id to the file
        :param p_object: int the id
        """
        with open(self.filename, 'a+') as f:
            f.write(str(p_object) + '\n')
