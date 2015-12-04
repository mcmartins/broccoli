from setuptools import setup
from sys import version
if version < '2.7.10':
    print 'Please update your python version to 2.7.10'
    exit(1)

setup(name='broccoli',
      version='0.0.1',
      description='Broccoli is a parallel tasks executor.',
      url='http://github.com/mcmartins/broccoli',
      author='Manuel Martins',
      author_email='manuelmachadomartins@gmail.com',
      license='Apache 2.0',
      packages=['broccoli', 'broccoli.schema', 'broccoli.test'],
      package_data={'broccoli': ['schema/*.json']},
      requires=['jsonschema'],
      install_requires=[
          'jsonschema'
      ],
      zip_safe=False)
