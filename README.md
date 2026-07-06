# muscles-data-sqlalchemy

SQLAlchemy adapter package for `muscles-data`.

This package is intentionally separate from `muscles-data`: the core package
owns typed ports, resource runtime and diagnostics, while this package owns the
SQLAlchemy-backed `SqlResourcePort` adapter.

Use this package when a project wants direct SQLAlchemy sessions through the
same data resource runtime without wiring `muscles-sql` first.

## Related packages

- Core runtime and port contracts:
  [`muscles-data`](https://github.com/butkoden/muscles-data)
- Elasticsearch search adapter:
  [`muscles-data-elasticsearch`](https://github.com/butkoden/muscles-data-elasticsearch)
- OpenSearch search adapter:
  [`muscles-data-opensearch`](https://github.com/butkoden/muscles-data-opensearch)
- Redis key-value/lock/stream adapter:
  [`muscles-data-redis`](https://github.com/butkoden/muscles-data-redis)
- Qdrant vector adapter:
  [`muscles-data-qdrant`](https://github.com/butkoden/muscles-data-qdrant)
- MongoDB document-store adapter:
  [`muscles-data-mongodb`](https://github.com/butkoden/muscles-data-mongodb)
- S3 object-store adapter:
  [`muscles-data-s3`](https://github.com/butkoden/muscles-data-s3)
- Executable example:
  [`example_data_sqlalchemy_1`](https://github.com/butkoden/muscular-example/tree/master/example_data_sqlalchemy_1)

## Usage

Register the factory in the project composition root:

```python
from muscles_data.catalog import DataAdapterCatalog
from muscles_data.ports import SqlResourcePort
from muscles_data.runtime import DataRuntime
from muscles_data_sqlalchemy import SqlAlchemySqlResourceFactory

catalog = DataAdapterCatalog.with_defaults()
catalog.register(SqlAlchemySqlResourceFactory())

runtime = DataRuntime(config=config, catalog=catalog)
sql = runtime.require_port("sql.local", SqlResourcePort)
```

Resource config stays in the project:

```yaml
data:
  resources:
    sql.local:
      type: sqlalchemy
      url: sqlite:///:memory:
      name: local_sqlite
      pool_pre_ping: true
      native_client: false
```

`data.resources.list` does not create the engine. The engine/session factory is
created lazily by `session()`, `session_factory()`, explicit native access or
`data.doctor`.

Application code should use `SqlResourcePort`; direct engine/session-factory
access is only an advanced escape hatch with `native_client: true`.

See `muscular-example/example_data_sqlalchemy_1` for an executable example.
