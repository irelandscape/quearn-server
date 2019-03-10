from steem.models import SteemUser

class SteemDBRouter(object):
    def db_for_read(self, model, **hints):
        if model == SteemUser:
            return ':memory'
        return None

    def db_for_write(self, model, **hints):
        if model == SteemUser:
            return ':memory'
        return None
