class NotToBeUsedException(Exception):
    pass


raise NotToBeUsedException("You should not be using this")
