#!/usr/bin/env python3

import os
from setuptools import find_packages, setup

setup(
    name="integreat_cms",
    version="0.0.13",
    packages=find_packages("backend"),
    package_dir={'':'backend'},
    include_package_data=True,
    scripts=['backend/integreat-cms'],
    data_files= [("lib/integreat-{}".format(root), [os.path.join(root, f) for f in files])
                 for root, dirs, files in os.walk('backend/cms/templates/')] +
                [("lib/integreat-{}".format(root), [os.path.join(root, f) for f in files])
                 for root, dirs, files in os.walk('backend/cms/static/')] +
                [('usr/lib/systemd/system/', ['systemd/integreat-cms@.service'])],
    install_requires=[
        "beautifulsoup4",
        "cffi",
        "Django==2.2.4",
        "django-filer",
        "django-mptt",
        "django-widget-tweaks",
        "djangorestframework",
        "drf-yasg",
        "idna",
        "lxml",
        "packaging",
        "psycopg2-binary",
        "pycryptodome",
        "python-dateutil",
        "requests",
        "rules",
        "six",
    ],
    extras_require={
        "dev": [
            "pylint==2.3.1",
            "pylint-django",
            "pylint_runner",
        ]
    },
    author="Integreat App Project",
    author_email="info@integreat-app.de",
    description="Content Management System for the Integreat App",
    license="GPL-2.0-or-later",
    keywords="Django Integreat CMS",
    url="http://github.com/Integreat/",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
