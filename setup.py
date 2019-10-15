#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


install_requires = [
    'setuptools',
    'django>=1.11',
]

setup(name='commons',
    version='1.0.0',
    description='Django Commons',
    long_description=open('README.rst').read(),
    keywords=['commons', 'django', 'utilities'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        Python :: Implementation :: CPython
        Python :: Implementation :: PyPy
        'Topic :: Office/Business',
    ],
    url='https://gitlab.com/zaade/django-commons',
    author='Ali Zaade',
    author_email='zaade.ali@gmail.com',
    license='MIT',
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    scripts=[],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    zip_safe=False
)

