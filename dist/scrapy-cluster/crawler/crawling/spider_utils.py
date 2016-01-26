__author__ = 'tomislav'
import functools


def standard_meta(response, add_dict={}):
    ret = {}
    ret['crawlid'] = response.meta['crawlid']
    ret['appid'] = response.meta['appid']
    ret['spiderid'] = response.meta['spiderid']
    ret['expires'] = 0
    ret['priority'] = response.meta['priority'] + 10  # so we go sooner to next depth
    ret.update(add_dict)
    return ret

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print 'Caught an exception in', f.__name__
            import subprocess
            subprocess.call(["sudo", "shutdown", "-h", "now"])
    return func
