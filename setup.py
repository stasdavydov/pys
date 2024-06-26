import pathlib
from distutils.core import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='py-s',
      version='0.0.2',
      description='Simple file storage for pydantic models, thread and multiprocess safe',
      long_description=README,
      long_description_content_type="text/markdown",
      url="https://github.com/stasdavydov/pys",
      author="Stas Davydov",
      author_email="davidovsv@yandex.ru",
      license="MIT",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Framework :: Pydantic",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.10",
          "Topic :: Database :: Database Engines/Servers",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=['pys'],
      include_package_data=False,
      install_requires=[
          'pydantic==2.7.4',
          'filelock==3.15.4',
      ],
      )
