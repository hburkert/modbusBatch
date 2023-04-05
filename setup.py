import setuptools
from modbusBatch.__init__ import VERSION

setuptools.setup( name='modbusBatch',
                  version=VERSION,
                  description='ModbusTCP layer for batched modbus requests',
                  long_description='ModbusTCP layer for batched modbus requests.',
                  url='https://github.com/hburkert/modbusBatch.git',
                  author='Heinz Burkert',
                  author_email='mail@heinz-burkert.com',
                  license='MIT',
                  packages=['modbusBatch'],
                  # packages=setuptools.find_packages(),
                  include_package_data=True,
                  zip_safe=False,
                  install_requires=['pyModbusTCP'],
                  python_requires='>=3.9.0'
                  )
