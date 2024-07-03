# Python Object Storage 

Simple fast JSON file storage for Python dataclasses and Pydantic models, thread and multiprocess safe. 

----

## Installation
```shell
pip install pysdato
```

## Usage
The library is intended to store Python dataclasses or Pydantic models as JSON-files referenced by ID 
and supports object hierarchy. 

Let's say we have `Author` model. Object's ID is key point for persistence -- it will be used as name of
file to store and load. We can have ID as object's field, but we may also keep it outside. 
The default expected name of ID field is `id`, but it can be changed with `id_field` 
parameter of `@saveable` decorator: `@saveable(id_field='email')`. 

```python
from dataclasses import dataclass
import pys

# Initialize storage with path where files will be saved
storage = pys.storage('.storage')

@pys.saveable
@dataclass
class Author:
    name: str

# Persist model Author
leo = Author(name='Leo Tolstoy')
leo_id = storage.save(leo)  # At this point the file `.storage/Author/<random uuid id>.json` will be saved
                            # with content {"name":"Leo Tolstoy"}

# Load model Author by its ID and check it's the same
another_leo = storage.load(Author, leo_id)
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

storage = pys.storage('.storage')

# A few books of Leo Tolstoy
leo = Author(name='Leo Tolstoy')
war_and_peace = Book(title='War and peace')

# Save Leo's book
leo_id = storage.save(leo)
wnp_id = storage.save(war_and_peace, leo)

# One more author :)
gpt = Author(name='Chat GPT')

# Do we have the same book by GPT?
gpt_war_and_peace = storage.load(Book, wnp_id, gpt)
assert gpt_war_and_peace is None

# Now it has :)
storage.save(war_and_peace, gpt)
gpt_war_and_peace = storage.load(Book, wnp_id, gpt)
assert gpt_war_and_peace is not None
```

We may have as many dependant models as we need. Actually, it's the way to have model dependent indexes
that let us easily faster get (dependent) model list by another model.
```python
from pydantic import BaseModel
import pys

# An author
@pys.saveable
class Author(BaseModel):
    name: str

# And a book
@pys.saveable
class Book(BaseModel):
    title: str

storage = pys.storage('.storage')

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

## Reference
```python
import pys

# Initialize storage
storage = pys.storage('.path-to-storage')

# Save a model with optional relation to other models
storage.save(model, [related_model | (RelatedModelClass, related_model_id), ...])

# Load a model by ModelClass and model_id with optional relation to other models
storage.load(ModelClass, model_id, [related_model | (RelatedModelClass, related_model_id), ...])

# Delete a model by ModelClass and model_id with optional relation to other models
storage.delete(ModelClass, model_id, [related_model | (RelatedModelClass, related_model_id), ...])

# List models by specified ModelClass with optional relation to other models
storage.list(ModelClass, [related_model | (RelatedModelClass, related_model_id), ...])
```
