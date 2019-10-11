import abc


class Product(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def locate(self, **kwargs):
        pass
