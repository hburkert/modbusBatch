from setuptools import setup
from modbusBatch.__init__ import VERSION

setup(name='modbusBatch',
      version=VERSION,
      description='ModbusTCP layer for batched modbus requests',
      long_description='ModbusTCP layer for batched modbus requests.',
      url='https://github.com/hburkert/modbusBatch.git',
      author='Heinz Burkert',
      author_email='mail@heinz-burkert.com',
      license='MIT',
      packages=['modbusBatch'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['pyModbusTCP']
      )
