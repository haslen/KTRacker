from setuptools import setup

setup(name='ktracker',
      version='0.1',
      description='Analysis of kinase translocation reporter data',
      url='http://github.com/haslen/ktracker',
      author='Nick Hasle',
      author_email='haslen@uw.edu',
      license='MIT',
      packages=['ktracker'],
      install_requires=['scipy', 'math', 'pandas', 'numpy', 'plotnine'],
      zip_safe=False)
