from django.db.models import JSONField, F
from django.db.models.functions import Cast
from wagtail.blocks import StreamValue

from wagtail_streamfield_migration_toolkit import utils


# TODO maybe a kwarg for batch size
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
):
    page_model = apps.get_model(app_name, model_name)
    updated_pages = []

    page_queryset = page_model.objects.annotate(
        raw_content=Cast(F(field_name), JSONField())
    ).all()
    for page in page_queryset.iterator():

        altered_raw_data = utils.apply_changes_to_raw_data(
            raw_data=page.raw_content,
            block_path_str=block_path_str,
            operation=operation,
            streamfield=getattr(page_model, field_name),
        )

        stream_block = getattr(page, field_name).stream_block
        setattr(
            page, field_name, StreamValue(stream_block, altered_raw_data, is_lazy=True)
        )

        updated_pages.append(page)

    page_model.objects.bulk_update(updated_pages, [field_name])

    # iterate over pages
    # - rename_blocks_in_raw_content for each page
    # - TODO add a return value to util to know if changes were made
    # - TODO save changed only
    # -
    # TODO for revisions
