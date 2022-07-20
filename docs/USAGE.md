## Making Custom Operations

While this package comes with a set of operations for common use cases, there may be many
instances where you need to define your own operation for mapping data. Making a custom operation
is fairly straightforward. All you need to do is extend the `BaseBlockOperation` class and 
define the `apply` method. 

For example, if we want to change the value of all child blocks of a specific type to "foo" and
the direct parent of each is a StreamBlock,

```
from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation

class MyBlockOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name
        
    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type] == self.name:
                mapped_block_value.append({**child_block, "value": "foo"})
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value
```

Note that we have to make sure that we are considering the correct type of direct parent when
defining the `apply` method, since the `block_value` argument passed depends on the type of 
parent we're dealing with.