
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

about = {}
with open('./__about__.py') as fp:
    exec(fp.read(), about)

config = {
    'description': 'Statistical Production Pipeline Engine',
    'author': about["__author__"],
    'author_email': about["__email__"],
    'url': about["__gitrepo__"],
    'download_url': about["__pkgrepo__"],
    'version': about["__version__"],
    'packages': ['aws', 'engine'],
    'scripts': [''],
    'name': 'spp_engine',
    'install_requires': [''],
    'classifiers': []
}