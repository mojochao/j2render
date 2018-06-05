"""j2render package setup module."""
import json

from setuptools import setup

with open('release.json') as infile:
    release_metadata = json.load(infile)

with open('requirements.txt') as infile:
    requirements = [line.strip() for line in infile.readlines()]

release_metadata.update(dict(
    py_modules=['j2render'],
    install_requires=requirements,
    zip_safe=True,
    test_suite='tests',
    entry_points={'console_scripts': [
        'j2render=j2render:cli',
    ]},))

setup(**release_metadata)
