# Wagtail streamfield-migration-toolkit

a set of reusable utilities to allow Wagtail implementors to easily generate data migrations for changes to StreamField block structure


[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[![PyPI version](https://badge.fury.io/py/streamfield-migration-toolkit.svg)](https://badge.fury.io/py/streamfield-migration-toolkit)
[![Wagtail Hallo CI](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml)

# Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Reference](docs/REFERENCE.md)
- [Usage](docs/USAGE.md)

# Introduction

This package aims to make it easier for developers using StreamField who need to write data 
migrations when making changes involving blocks/block structure in the StreamField. We expose a 
set of utilities for commonly made changes such as renaming or removing blocks, as well as utility
functions for recursing through existing Streamfield data and applying changes, which makes it 
easier to create custom logic for applying changes too.

# Quick Start

## Installation

- `pip install streamfield-migration-toolkit`
- Add `"wagtail_streamfield_migration_toolkit"` to `INSTALLED_APPS`

## Supported versions

- Python 3.7, 3.8, 3.9
- Django 3.2, 4.0
- Wagtail 3.0

## Sample Usage

```
from django.db import migrations

from wagtail_streamfield_migration_toolkit.funcs import migrate_stream_data
from wagtail_streamfield_migration_toolkit.operations import RenameStreamChildrenOperation


def forward(apps, schema_editor):
    # to rename block "field1" to "block1"
    migrate_stream_data(
        apps=apps,
        schema_editor=schema_editor,
        app_name="blog",
        model_name="BlogPage",
        field_name="content",
        block_path_str="field1",
        operation=RenameStreamChildrenOperation(new_name="block1"),
        with_revisions=False,
        revision_limit=None,
        chunk_size=1024
    )


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ...
    ]

    operations = [migrations.RunPython(forward, backward)]

```
