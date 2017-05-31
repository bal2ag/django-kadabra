"""
Django-Kadabra
-------------

Django middleware for the Kadabra metrics framework.
"""
import ast, re

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('django_kadabra/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='Django-Kadabra',
    version=version,
    url='https://github.com/bal2ag/django-kadabra',
    #license='BSD',
    author='Alex Landau',
    author_email='balexlandau@gmail.com',
    description='Django middleware for the Kadabra metrics framework',
    long_description=__doc__,
    py_modules=['django_kadabra'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Django>=1.11',
        'Kadabra>=0.4.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
