class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'app_aws_db':
            return "storage"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'app_aws_db':
            return "storage"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        return True

    def allow_migrate(self, db, app_label, model=None, **hints):
        return True
