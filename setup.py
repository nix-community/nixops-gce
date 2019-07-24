import sys
import subprocess

from distutils.core import setup, Command

setup(name='nixops-gce',
      version='@version@',
      description='NixOps backend for Google Cloud',
      url='https://github.com/AmineChikhaoui/nixops-gce',
      maintainer='Amine Chikhaoui',
      maintainer_email='amine.chikhaoui91@gmail.com',
      packages=['nixopsgce', 'nixopsgce.backends', 'nixopsgce.resources'],
      entry_points={'nixops': ['gce = nixopsgce.plugin']},
      py_modules=['plugin']
)
