import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

PYTEST_VERSION = '8.22'
PYDANTIC_VERSION = '2.0'
FILELOCK_VERSION = '3.15.4'
MSGSPEC_VERSION = '0.18.6'

setup(name='pysdato',
      version='0.0.12',
      python_requires='>=3.9',
      description='Simple JSON file storage for Python dataclasses, msgspec structs and pydantic models, thread and '
                  'multiprocess safe',
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
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "Topic :: Database :: Database Engines/Servers",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=['pys'],
      include_package_data=False,
      install_requires=[
          f'filelock >= {FILELOCK_VERSION}',
          f'msgspec >= {MSGSPEC_VERSION}',
      ],
      extras_require={
          'test': [
              f'pytest >= {PYTEST_VERSION}',
              f'msgspec >= {MSGSPEC_VERSION}',
              f'pydantic >= {PYDANTIC_VERSION}',
          ],
          'dataclass': [
              f'msgspec >= {MSGSPEC_VERSION}',
          ],
          'msgspec': [
              f'msgspec >= {MSGSPEC_VERSION}',
          ],
          'pydantic': [
              f'pydantic >= {PYDANTIC_VERSION}',
          ],
      }
      )
