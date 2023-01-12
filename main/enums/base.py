class EnumBase:
    @classmethod
    def get_list(cls):
        return [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]
