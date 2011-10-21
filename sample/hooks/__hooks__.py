import logging

hooks = {
    'page.template.pre': []
}

try:
    import wok_sample_hooks
    hooks['page.render.pre'].append(wok_sample_hooks.import_hook)
except:
    logging.warning("Failed to import hook.")

def basic_hook(page, templ_vars):
    logging.info('basic_hook got page {0[slug]}.'.format(page))

hooks['page.template.pre'].append(basic_hook)

logging.info('Got hooks: {0}'.format(hooks))
