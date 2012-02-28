from setuptools import setup, find_packages

setup(
    name='rpush',
    version='0.1',
    description='Job Queue Push Notification',
    author='rizkyabdilah',
    author_email='rizky@abdi.la',
    install_requires=['web.py', 'redis'],
    zip_safe=True,
)