from setuptools import setup

setup(name='python-cah',
      version='0.1b0',
      description='',
      author='Alexis Lameire',
      author_email='alexis.lameire@gmail.com',
      url='https://github.com/alexises/python-cah',
      packages=['pythonCah', 'pythonCah.irc'],
      install_requires=['marshmallow'],
      tests_require=['pytest'],
      setup_requires=['pytest-runner']
)
