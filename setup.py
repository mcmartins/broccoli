from setuptools import setup
import sys

# check for if the python version can run broccoli
current_version = sys.version_info

if current_version < (2, 7, 5):
    sys.exit('Sorry. Please update your python version to match range >=2.7.5.')

# setup
setup(name='broccoli',
      version='0.0.2',
      description='Broccoli is a parallel Jobs executor.',
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
