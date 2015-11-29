import logging
from wok.contrib.hooks import compile_sass

hook_count = 0
def make_hook(name):
    def logging_hook(*args):
        global hook_count
        logging.info('logging_hook: {0}: {1}'.format(name, hook_count))
        hook_count += 1
    return [logging_hook]

hooks = {
    'site.start': make_hook('site.start'),
    'site.output.pre': make_hook('site.output.pre'),
    'site.output.post': [compile_sass],
    'site.content.gather.pre': make_hook('site.content.gather.pre'),
    'site.content.gather.post': make_hook('site.content.gather.post'),
    'page.meta.pre': make_hook('page.template.pre'),
    'page.meta.post': make_hook('page.template.post'),
    'page.render.pre': make_hook('page.template.pre'),
    'page.render.post': make_hook('page.template.post'),
    'page.template.pre': make_hook('page.template.pre'),
    'page.template.post': make_hook('page.template.post'),
    'site.stop': make_hook('site.stop'),
}

logging.info('loaded hooks.')
