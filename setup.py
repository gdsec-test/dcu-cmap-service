from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()

with open('test_requirements.txt') as f:
    testing_reqs = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(
    name='cmap_service',
    version='1.0',
    author='DCU',
    author_email='dcueng@godaddy.com',
    description='Provides enrichment for domain names and IP addresses',
    long_description=long_description,
    url='https://github.secureserver.net/ITSecurity/cmap_service',
    packages=find_packages(exclude=['tests', 'trusted_certs']),
    install_requires=install_reqs,
    tests_require=testing_reqs,
    test_suite='nose.collector',
    classifiers=[
        'Programming Language :: Python :: 2.7'
    ]
)
