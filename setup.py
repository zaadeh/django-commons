#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()

install_requires = [
    'setuptools',
    'django>=1.11',
    'pytz',
    'bleach',
    'jdatetime',
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Natural Language :: English',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Framework :: Django',
]

setup(name='django-commons',
    version='0.1.2',
    description='Common Django Utilities',
    long_description=long_description,
    keywords=['commons', 'django', 'utilities'],
    classifiers=classifiers,
    author='Ali Zaade',
    author_email='zaadeh.ali@gmail.com',
    url='https://gitlab.com/zaade/django-commons',
    license='GPLv3+',
    platforms='any',
    packages=find_packages(),
    #  package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=install_requires,
    scripts=[],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    zip_safe=False
)
