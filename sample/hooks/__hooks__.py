import logging

hooks = {
    'page.template.pre': []
}

import wok_sample_hooks
hooks['page.template.pre'].append(wok_sample_hooks.import_hook)

hook_count = 0
def basic_hook(page, templ_vars):
    global hook_count
    logging.info('basic_hook got page {0[slug]}.'.format(page))
    templ_vars['hooked'] = hook_count
    hook_count += 1

hooks['page.template.pre'].append(basic_hook)

logging.info('Got hooks: {0}'.format(hooks))
