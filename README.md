# Python Storage
Simple file storage for `pydantic` models, thread and multiprocess safe 

## Installation
```shell
pip install pys
```

## Usage
PyS is intended to store `pydantic` models as files referenced by ID and some hierarchy. 
Let's say we have `A` model:

### Model
```python
from pydantic import BaseModel

class A(BaseModel):
    id: str
    name: str
    rate: float
```

Instead of `BaseModel` we can extend from `ModelWithID` from `pys` for convenience.  
`ModelWithID` defines `id` field automatically initialized with random UUID, so we don't need to initialize
it manually. Then we can save it and load it.

### Saving and loading
```python
import pys

# Initialize storage with path where files will be saved
storage = pys.storage('.storage')

class Author(pys.ModelWithID):
    name: str

# Persist model Author
leo = Author(name='Leo Tolstoy')
storage.save(leo)

# Load model Author by its ID and check it's the same
another_leo = storage.load(Author, leo.id)
assert another_leo.id == leo.id
assert another_leo.name == leo.name
```

### Work with dependant models
We may have a model that has list of other models (like Authors and their Books). We can work with
that dependant models separately (as we did before with model `Author`), but we can also persist these
models in context of their primary model.

```python
import pys

# An author
class Author(pys.ModelWithID):
    name: str

# And a book
class Book(pys.ModelWithID):
    title: str

storage = pys.storage('.storage')

# Most famous book of Leo Tolstoy
leo = Author(name='Leo Tolstoy')
war_and_peace = Book(title='War and peace')

# Save Leo's book
storage.save(leo)
storage.save(war_and_peace, leo)

# One more author :)
gpt = Author(name='Chat GPT')

# Do we have the same book by GPT?
gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
assert gpt_war_and_peace is None

# Now it has :)
storage.save(war_and_peace, gpt)
gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
assert gpt_war_and_peace is not None
```

We may have as many dependant models as we need. Actually, it's the way to have model dependent indexes
that let us easily faster get (dependent) model list by another model.
```python
import pys

# An author
class Author(pys.ModelWithID):
    name: str

# And a book
class Book(pys.ModelWithID):
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

