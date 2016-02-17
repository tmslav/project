__author__ = 'tomislav'


def standard_meta(response, add_dict={}):
    ret = {}
    ret['crawlid'] = response.meta['crawlid']
    ret['appid'] = response.meta['appid']
    ret['spiderid'] = response.meta['spiderid']
    ret['expires'] = 0
    ret['priority'] = response.meta['priority'] + 10  # so we go sooner to next depth
    ret.update(add_dict)
    return ret
