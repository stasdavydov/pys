# Python Object Storage 

Simple fast JSON file storage for Python dataclasses and Pydantic models, thread and multiprocess safe. 

[![PyPI](https://img.shields.io/pypi/v/pysdato)](https://pypi.org/project/pysdato/)
[![Supported Python
versions](https://img.shields.io/pypi/pyversions/pysdato.svg)](https://pypi.org/project/pysdato/)

----
It's standard to use SQL or NoSQL database servers as data backend, but sometimes it's more
convenient to have data persisted as file(s) locally on backend application side. If you still
need to use SQL for data retrieval the best option is SQLite, but for simple REST APIs it 
could be better to work with objects as is. So here we go.

## Installation
```shell
pip install pysdato
```

If you plan to use it with `pydantic`:
```shell
pip install pysdato[pydantic]
```

To use with dataclasses:
```shell
pip install pysdato[dataclass]
```

To use with `msgspec`:
```shell
pip install pysdato[msgspec]
```


## Usage
The library is intended to store Python `dataclasses`, `msqspec.Struct` or Pydantic models as JSON-files referenced by ID 
and supports object hierarchy. 

Let's say we have `Author` model. Object's ID is key point for persistence -- it will be used as name of
file to store and load. We can have ID as object's field, but we may also keep it outside. 
The default expected name of ID field is `id`, but it can be changed with `id_field` 
parameter of `@saveable` decorator: `@saveable(id_field='email')`. 

```python
from dataclasses import dataclass
import pys

# Initialize storage with path where files will be saved
storage = pys.storage('storage.db')

@pys.saveable
@dataclass
class Author:
    name: str

# Persist model Author
leo = Author(name='Leo Tolstoy')
storage.save(leo)  # At this point the file `.storage/Author/<random uuid id>.json` will be saved
                   # with content {"name":"Leo Tolstoy"}

# Load model Author by its ID and check it's the same
another_leo = storage.load(Author, leo.__my_id__())
assert another_leo.name == leo.name
```

### Work with dependant data
We may have a class that relates to other classes (like Authors and their Books). We can persist
that dependant class separately (as we did before with `Author`), but we can also persist 
in context of their "primary" class.

```python
import pys
from pydantic import BaseModel

# An author
@pys.saveable
class Author(BaseModel):
    name: str

# And a book
@pys.saveable
class Book(BaseModel):
    title: str

storage = pys.storage('storage.db')

# A few books of Leo Tolstoy
leo = Author(name='Leo Tolstoy')
war_and_peace = Book(title='War and peace')

# Save Leo's book
storage.save(leo)
storage.save(war_and_peace, leo)

# One more author :)
gpt = Author(name='Chat GPT')

# Do we have the same book by GPT?
gpt_war_and_peace = storage.load(Book, war_and_peace.__my_id__(), gpt)
assert gpt_war_and_peace is None

# Now it has :)
storage.save(war_and_peace, gpt)
gpt_war_and_peace = storage.load(Book, war_and_peace.__my_id__(), gpt)
assert gpt_war_and_peace is not None
```

We may have as many dependant models as we need. Actually, it's the way to have model dependent indexes
that let us easily get (dependent) model list by another model.
```python
import pys
from pys.pydantic import ModelWithID

# An author
class Author(ModelWithID):
    name: str

# And a book
class Book(ModelWithID):
    title: str

storage = pys.storage('storage.db')

# A few books of Leo Tolstoy
leo = Author(name='Leo Tolstoy')
war_and_peace = Book(title='War and peace')
for_kids = Book(title='For Kids')

storage.save(leo)
storage.save(war_and_peace, leo)
storage.save(for_kids, leo)

leo_books = list(storage.list(Book, leo))
assert len(leo_books) == 2
assert war_and_peace in leo_books
assert for_kids in leo_books
```

### More samples
Please check `tests/test_samples.py` for more saveable class definitions and operations.

## Storages
Library supports two storages implementation: 
- `sqlite_storage()` - SQLite based -- really fast, uses one file for all objects.
- `file_storage()` - JSON file per object storage, it is slower, but saves each object in a separate JSON file.

The default storage is SQLite based.

## Library Reference
```python
import pys

# Initialize file storage
storage = pys.file_storage('.path-to-storage')

# Initialize SQLite (default) storage
storage = pys.storage('path-to-storage.db')
storage = pys.sqlite_storage('path-to-storage.db')

# Save a model with optional relation to other models
storage.save(model, [related_model | (RelatedModelClass, related_model_id), ...])

# Load a model by ModelClass and model_id with optional relation to other models
storage.load(ModelClass, model_id, [related_model | (RelatedModelClass, related_model_id), ...])

# Delete a model by ModelClass and model_id with optional relation to other models
storage.delete(ModelClass, model_id, [related_model | (RelatedModelClass, related_model_id), ...])

# List models by specified ModelClass with optional relation to other models
storage.list(ModelClass, [related_model | (RelatedModelClass, related_model_id), ...])

# Destroy storage
storage.destroy()
```

## Benchmark
You can find the benchmark code in `benchmark.py` file.

```
Storage: file.Storage(base_path=benchmark.storage)
T1: 679.41 ms -- save 1100 objects -- 0.618 ms per object
T3: 1657.14 ms -- list 500 objects -- 3.314 ms per object
T4: 1284.38 ms -- list 500 objects -- 2.569 ms per object
Storage: sqlite.Storage(base_path=benchmark.db)
T1: 18.52 ms -- save 1100 objects -- 0.017 ms per object
T3: 6.00 ms -- list 500 objects -- 0.012 ms per object
T4: 1.00 ms -- list 500 objects -- 0.002 ms per object
```

## Release Notes
- **0.0.12** Fixed: issue with file encoding for custom raw models.
- **0.0.11** Fixed: use own `__my_id__()` function if defined in data class.
- **0.0.10** Minor changes in documentation.
- **0.0.9** improved performance, generic `Persistent` base class is provided for custom implementations,
  allowed installing specifically for pydantic, dataclasses or msgspec usage.
- **0.0.8** unit-test covers more cases now. Object's actual ID can be used even if it's not defined. 
  Documentation is updated. 
- **0.0.7** build and test for different Python versions.
- **0.0.6** `saveable` decorator reworked, added `default_id` parameter that can be used for
changing ID generation behaviour. By default, we use `str(uuid.uuid4())` as ID.
- **0.0.5** Performance is dramatically improved with SQLite storage implementation. 
Default storage is SQLite storage now.
- **0.0.4** SQLite storage is added. Support of `msqspec` JSON and structures is added.
- **0.0.3** Benchmark is added, performance is improved. Fixed dependency set up.
- **0.0.2** Added support for Python 3.x < 3.10
- **0.0.1** Initial public release
