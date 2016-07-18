import time
from functools import partial
import json

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

levels = Enum(('w', 'i', 'e', 'v'))

_supressed_tags = set()
_supressed_levels = set()
_sav = []

def log(tag, s, pretty, level, save=True):
    if save:
        _sav.append((time.strftime('%H:%M:%S'), level, tag, s))
    if tag in _supressed_tags or level in _supressed_levels:
        return
    print(pretty.format(time=time.strftime('%H:%M:%S'), tag=tag, msg=s))

pretty_warning = (
    '\033[43;30mWARN\033[0m {time} \033[4m{tag}\033[0;1m\t{msg}\033[0m')
pretty_information = (
    '\033[42;30mINFO\033[0m {time} \033[4m{tag}\033[0;1m\t{msg}\033[0m')
pretty_error = (
    '\033[41;37mEROR\033[0m {time} \033[4m{tag}\033[0;1m\t{msg}\033[0m')
pretty_verbose = (
    '\033[47;30mVERB\033[0m {time} \033[4m{tag}\033[0;1m\t{msg}\033[0m')

w = partial(log, pretty=pretty_warning, level=levels.w)
i = partial(log, pretty=pretty_information, level=levels.i)
e = partial(log, pretty=pretty_error, level=levels.e)
v = partial(log, pretty=pretty_verbose, level=levels.v)

def supress_tag(tag):
    _supressed_tags.add(tag)

def supress_level(level):
    _supressed_levels.add(level)

def unsupress_tag(tag):
    _supressed_tags.discard(tag)

def unsupress_level(level):
    _supressed_levels.discard(level)

def unsupress_all_tags():
    _supressed_tags.clear()

def unsupress_all_levels():
    _supressed_levels.clear()

def output(*s, sep=' ', end='\n', file=None, flush=False):
    v('print', sep.join(map(lambda x: str(x), s)))

def save(filename=None, supressed_tags=None,
         supressed_levels=None, prompt=True):
    if filename == None:
        filename = './mlogger_%s.log' % (time.strftime('%Y_%m_%d_%H_%M_%S'))
    if (supressed_tags or supressed_levels) == None:
        with open(filename, 'w') as f:
            json.dump(_sav, f, ensure_ascii=False, indent=4)
    else:
        if supressed_levels == 'default':
            supressed_levels = _supressed_levels
        if supressed_tags == 'default':
            supressed_tags = _supressed_tags
        supressed_levels = supressed_levels or ()
        supressed_tags = supressed_tags or ()

        s = [i for i in _sav
            if not(i[1] in supressed_levels or i[2] in supressed_tags)]
        with open(filename, 'w') as f:
            json.dump(s, f, ensure_ascii=False, indent=4)
    if prompt:
        i('logger', 'Save file created: '+filename, save=False)


if __name__ == '__main__':
    # for test only
    w('tag', 'this is a warning')
    i('tag', 'this is an information')
    e('tag', 'this is an error')
    v('tag', 'this is a verbose man')

    i('tag', 'you can see me here but not in the save file.', save=False)
    supress_level(levels.w)
    w('tag', 'you cannot see me')

    supress_tag('awful')
    i('awful', 'you cannot see me')

    unsupress_level(levels.w)
    unsupress_tag('awful')
    w('awful', 'glad you can see me')

    save()
