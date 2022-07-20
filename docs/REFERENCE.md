# Contents

- [Migrate Stream Data](#migrate-stream-data)
- [Operations](#operations)
  - [Rename Operations](#rename-operations)
  - [Remove Operations](#remove-operations)

# Migrate Stream Data

`from wagtail_streamfield_migration_toolkit.funcs import migrate_stream_data`

This function is responsible for querying the relevant models, recursing through stream data to 
map it and saving the updated stream data. It works by taking a block path which points to the 
direct parent of the blocks which should be matched when making changes and an operation which 
defines how old data (child blocks) is mapped to the new data.

```
def migrate_stream_data(
    apps,
    schema_editor,
    app_name,
    model_name,
    field_name,
    block_path_str,
    operation,
    with_revisions=False,
    revision_limit=None,
    chunk_size=1024,
)
```

## Parameters

### apps
### schema_editor

Args which are passed to the forward function of a django `migrations.RunPython` operation. 
Refer [here](https://docs.djangoproject.com/en/4.0/howto/writing-migrations/#data-migrations-and-multiple-databases)

### app_name

**String**. Name of the app which contains the relevant model. 

### model_name

**String**. Name of the model which contains the relevant streamfield.

### field_name

**String**. The name of the streamfield to which changes are to be made.

If we are changing the streamfield `content` in the model `BlogPage` in the app `blog`, then

`..., app_name="blog", model_name="BlogPage", field_name="content", ...`

### block_path_str

**String**. This should be `None` if changes are being made to a toplevel block, otherwise a "."
separated string of block names which points to the direct parent of the block/s being altered.
The `value` (that is the children) of each matching block is passed to the operation class to be
altered. For example, if our stream definition looks like this,

```
class MyDeepNestedBlock(StreamBlock):
    foo = CharBlock()
    date = DateBlock()

class MyNestedBlock(StreamBlock): 
    char1 = CharBlock()
    deepnested1 = MyDeepNestedBlock()

class MyStreamBlock(StreamBlock):
    field1 = CharBlock()
    nested1 = MyNestedBlock()
```
Then if we want to alter field1 which is a top level block, we pass `block_path_str=None` which 
matches the value of the streamfield itself

```
[
    { "type": "field1", ... }, 
    { "type": "field1", ... }, 
    { "type": "nested1", ... },
    ...
] # This entire list is passed to operation
```

And if we want to alter "char1" which is a direct child of "nested1", we pass 
`block_path_str="nested1"` which matches all "nested1" blocks

```
[
    { "type": "field1", ... },
    { "type": "field1", ... },
    { "type": "nested1", "value": [...] }, # This is matched 
    { "type": "nested1", "value": [...] }, # This is matched
    ...
]
```

And if we want to alter "foo" which is a direct child of "deepnested1", we pass 
`block_path_str="nested1.deepnested1"` which matches all "deepnested1" blocks

```
[
    { "type": "field1", ... },
    { "type": "field1", ... },
    { "type": "nested1", "value": [
        { "type": "char1", ... },
        { "type": "deepnested1", ... }, # This is matched
        { "type": "deepnested1", ... }, # This is matched
        ...
    ] },
    { "type": "nested1", "value": [
        { "type": "char1", ... },
        { "type": "deepnested1", ... }, # This is matched
        ...
    ] },
    ...
]
```

**NOTE**: When the path contains a ListBlock child, 'item' must be added to the block path as
the name of said child. For example, if we consider the following stream definition,

```
class MyStructBlock(StructBlock): 
    char1 = CharBlock()
    char2 = CharBlock()

class MyStreamBlock(StreamBlock):
    list1 = ListBlock(MyStructBlock())
```

Then if we want to alter "char1", which is a child of the structblock which is the direct list 
child, we have to use `block_path_str="list1.item"` instead of ~~`block_path_str="list1"`~~. We 
can also match the ListBlock child as such if we want with `block_path_str="list1"`.

### operation

**[Operation](#operations)**. This is basically an object which has a method for mapping matched
blocks.

### with_revisions

**Boolean**. Determines whether page revision data should be migrated too. Defaults to `false`.

### revision_limit

**Integer | None**. If migrating revision data, to limit to the last `revision_limit` number of 
revisions. If this is `None`, migrates all revisions. Defaults to `None`.

### chunk_size

**Integer**. Determines the chunk size which is read at a time when querying and when updating in 
the database. This may affect speed and memory usage. Generally the default values work fine.
Defaults to 1024.


# Operations

`from wagtail_streamfield_migration_toolkit import operations`

An Operation class contains the logic for mapping old data to new data. All Operation classes 
should extend the `BaseBlockOperation` class.

An Operation class has an `apply` method which determines how changes are applied to the
block/s we want to change. This method is called for the value of all blocks matching the given 
block path (`block_path_str`). 

```
    def apply(self, block_value):
```

### block_value

The value of matching blocks is passed as an argument to the `apply` method, which is responsible 
for applying changes to the children of the matching blocks and returning the altered values. 
Note that **we are dealing with raw data here**, not block objects, so our values have a JSON like 
structure, similar to what `StreamValue().raw_data` gives. 

The value passed to `apply` when the parent is a StreamBlock would look like this,

```
[
    { "type": "...", "value": "...", "id": "..." },
    { "type": "...", "value": "...", "id": "..." },
    ...
]
```

The value passed to `apply` when the parent is a StructBlock would look like this,

```
{
    "name1": "...",
    "name2": "...",
    ...
}
```

The value passed to `apply` when the parent is a ListBlock would look like this,

```
[
    { "type": "item", "value": "...", "id": "..." },
    { "type": "item", "value": "...", "id": "..." },
    ...
]
```

The following operations are available and can be imported from 
`wagtail_streamfield_migration_toolkit.operations`.

## Rename Operations

- RenameStreamChildrenOperation
- RenameStructChildrenOperation

### Params:

- old_name : **String**. The name of blocks that must be renamed.
- new_name : **String**. The name which the blocks must be renamed to.

### Sample Usage:

```
migrate_stream_data(
    ...,
    operation=RenameStreamChildrenOperation(old_name="char1", new_name="CoolName"),
    ...
)
```

## Remove Operations

- RemoveStreamChildrenOperation
- RemoveStructChildrenOperation

### Sample Usage:

```
migrate_stream_data(
    ...,
    operation=RemoveStreamChildrenOperation(),
    ...
)
```

<!-- CombineToListBlock -->
<!-- CombineToStreamBlock -->
<!-- AddDefaultValue -->

It is possible to make your own custom operations by extending the `BaseBlockOperation` class 
and defining the `apply` method as needed. Refer [here](USAGE.md#making-custom-operations) 
for examples.
