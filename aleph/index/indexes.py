import logging
from banal import ensure_list
from followthemoney import model
from followthemoney.types import registry

from aleph.core import settings
from aleph.index.util import index_settings, configure_index

log = logging.getLogger(__name__)


DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd||yyyy-MM||yyyy"
PARTIAL_DATE = {"type": "date", "format": DATE_FORMAT}
LATIN_TEXT = {"type": "text", "analyzer": "icu_latin"}
RAW_TEXT = {"type": "text"}
KEYWORD = {"type": "keyword"}
LATIN_KEYWORD = {"type": "keyword", "normalizer": "icu_latin"}
TYPE_MAPPINGS = {
    registry.text: LATIN_TEXT,
    registry.date: PARTIAL_DATE,
}


def collections_index():
    """Combined index to run all queries against."""
    return settings.COLLECTIONS_INDEX


def all_indexes():
    return ','.join((collections_index(),
                     entities_read_index(),
                     records_read_index()))


def configure_collections():
    mapping = {
        "date_detection": False,
        "dynamic_templates": [
            {
                "fields": {
                    "match": "schemata.*",
                    "mapping": {"type": "long"}
                }
            }
        ],
        "_source": {
            "excludes": ["text"]
        },
        "properties": {
            "label": {
                "type": "text",
                "analyzer": "icu_latin",
                "fields": {"kw": KEYWORD}
            },
            "collection_id": KEYWORD,
            "foreign_id": KEYWORD,
            "languages": KEYWORD,
            "countries": KEYWORD,
            "category": KEYWORD,
            "summary": RAW_TEXT,
            "publisher": KEYWORD,
            "publisher_url": KEYWORD,
            "data_url": KEYWORD,
            "info_url": KEYWORD,
            "kind": KEYWORD,
            "text": LATIN_TEXT,
            "casefile": {"type": "boolean"},
            "secret": {"type": "boolean"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "count": {"type": "long"},
            "schemata": {"type": "object"},
            "creator": {
                "type": "object",
                "properties": {
                    "id": KEYWORD,
                    "type": KEYWORD,
                    "name": {
                        "type": "text",
                        "fields": {"kw": KEYWORD}
                    }
                }
            },
            "team": {
                "type": "object",
                "properties": {
                    "id": KEYWORD,
                    "type": KEYWORD,
                    "name": KEYWORD
                }
            },
        }
    }
    configure_index(collections_index(), mapping, index_settings())


def records_write_index():
    """Index that us currently written by new queries."""
    return settings.RECORDS_INDEX


def records_read_index():
    """Combined index to run all queries against."""
    return ','.join(settings.RECORDS_INDEX_SET)


def configure_records():
    mapping = {
        "date_detection": False,
        "properties": {
            "collection_id": KEYWORD,
            "document_id": KEYWORD,
            "index": {"type": "long"},
            "text": {
                "type": "text",
                "analyzer": "icu_latin",
                "term_vector": "with_positions_offsets"
            },
        }
    }
    settings = index_settings(shards=10, refresh_interval='15s')
    configure_index(records_write_index(), mapping, settings)


def schema_index(schema):
    """Convert a schema object to an index name."""
    return '-'.join((settings.ENTITIES_INDEX, schema.name.lower()))


def entities_write_index(schema):
    """Index that us currently written by new queries."""
    if not settings.ENTITIES_INDEX_SPLIT:
        return settings.ENTITIES_INDEX

    return schema_index(model.get(schema))


def entities_read_index(schema=None, descendants=True, exclude=None):
    """Combined index to run all queries against."""
    if not settings.ENTITIES_INDEX_SPLIT:
        indexes = set(settings.ENTITIES_INDEX_SET)
        indexes.add(settings.ENTITIES_INDEX)
        return ','.join(indexes)

    schemata = set()
    names = ensure_list(schema) or model.schemata.values()
    for schema in names:
        schema = model.get(schema)
        if schema is None:
            continue
        schemata.add(schema)
        if descendants:
            schemata.update(schema.descendants)
    exclude = model.get(exclude)
    indexes = list(settings.ENTITIES_INDEX_SET)
    for schema in schemata:
        if not schema.abstract and schema != exclude:
            indexes.append(schema_index(schema))
    # log.info("Read index: %r", indexes)
    return ','.join(indexes)


def configure_entities():
    if not settings.ENTITIES_INDEX_SPLIT:
        return configure_schema(None)
    for schema in model.schemata.values():
        if not schema.abstract:
            configure_schema(schema)


def configure_schema(schema):
    # Generate relevant type mappings for entity properties so that
    # we can do correct searches on each.
    schema_mapping = {}
    if settings.ENTITIES_INDEX_SPLIT:
        for name, prop in schema.properties.items():
            config = dict(TYPE_MAPPINGS.get(prop.type, KEYWORD))
            config['copy_to'] = 'text'
            schema_mapping[name] = config

    mapping = {
        "date_detection": False,
        "_source": {
            "excludes": ["text", "fingerprints"]
        },
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "icu_latin",
                "fields": {"kw": KEYWORD},
                "boost": 3.0,
                "copy_to": "text"
            },
            "schema": KEYWORD,
            "schemata": KEYWORD,
            "bulk": {"type": "boolean"},
            "status": KEYWORD,
            "error_message": RAW_TEXT,
            "content_hash": KEYWORD,
            "foreign_id": KEYWORD,
            "file_name": KEYWORD,
            "collection_id": KEYWORD,
            "uploader_id": KEYWORD,
            "source_url": KEYWORD,
            "extension": KEYWORD,
            "mime_type": KEYWORD,
            "entities": KEYWORD,
            "languages": KEYWORD,
            "countries": KEYWORD,
            "keywords": KEYWORD,
            "fingerprints": LATIN_KEYWORD,
            "names": {
                "type": "keyword",
                "fields": {"text": LATIN_TEXT},
                "copy_to": "text"
            },
            "emails": KEYWORD,
            "phones": KEYWORD,
            "identifiers": KEYWORD,
            "addresses": {
                "type": "keyword",
                "fields": {"text": LATIN_TEXT}
            },
            "columns": KEYWORD,
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "date": PARTIAL_DATE,
            "authored_at": PARTIAL_DATE,
            "modified_at": PARTIAL_DATE,
            "published_at": PARTIAL_DATE,
            "retrieved_at": PARTIAL_DATE,
            "dates": PARTIAL_DATE,
            "author": KEYWORD,
            "generator": KEYWORD,
            "summary": RAW_TEXT,
            "text": {
                "type": "text",
                "analyzer": "icu_latin",
                "term_vector": "with_positions_offsets",
                "store": True
            },
            "properties": {
                "type": "object",
                "properties": schema_mapping
            },
            "parent": {
                "type": "object",
                "properties": {
                    "id": KEYWORD,
                    "type": KEYWORD,
                    "title": KEYWORD
                }
            },
            "ancestors": KEYWORD,
        }
    }
    index = entities_write_index(schema)
    configure_index(index, mapping, index_settings())
