from setuptools import setup
from os.path import dirname, join

setup(
  name="b2cm",
  version="1.0",
  author="Russell Hay",
  author_email="me@russellhay.com",
  description="a script that converts cinderblock.xml files into cmake functions allowing easier use of cinder with cmake",
  license="MIT",
  py_modules=["b2cm"],
  entry_points={
      "console_scripts": [
          "b2cm = b2cm:main"
      ]
  },
  install_requires=[ 'mako==1.0.1' ]
)
