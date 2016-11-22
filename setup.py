#!/usr/bin/env python2

from setuptools import setup

from wok import version

setup(
    name='wok',
    version=version.encode("utf8"),
    author='Mike Cooper',
    author_email='mythmon@gmail.com',
    url='http://wok.mythmon.com',
    description='Static site generator',
    long_description=
        "Wok is a static website generator. It turns a pile of templates, "
        "content, and resources (like CSS and images) into a neat stack of "
        "plain HTML. You run it on your local computer, and it generates a "
        "directory of web files that you can upload to your web server, or "
        "serve directly.",
    download_url="http://wok.mythmon.com/download",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    install_requires=[
        'Jinja2==2.6',
        'Markdown==2.6.5',
        'PyYAML==3.10',
        'Pygments==2.1',
        'docutils==0.8.1',
        'awesome-slugify==1.4',
        'pytest==2.5.2',
    ],
    packages=['wok'],
    package_data={'wok':['contrib/*']},
    scripts=['scripts/wok'],
)
