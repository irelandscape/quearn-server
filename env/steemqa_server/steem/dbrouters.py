from steem.models import AccessToken

class SteemDBRouter(object):
    def db_for_read(self, model, **hints):
        if model == AccessToken:
            return ':memory'
        return None

    def db_for_write(self, model, **hints):
        if model == AccessToken:
            return ':memory'
        return None
