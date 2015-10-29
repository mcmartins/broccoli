from setuptools import setup

setup(name='broccoli',
      version='0.0.1',
      description='Broccoli is a parallel tasks executor.',
      url='http://github.com/mcmartins/broccoli',
      author='Manuel Martins',
      author_email='manuelmachadomartins@gmail.com',
      license='Apache 2.0',
      packages=['broccoli'],
      zip_safe=False, requires=['jsonschema'])
