# `muscles-data-sqlalchemy` RC checklist

The package ships the SQLAlchemy implementation of `SqlResourcePort`.
The dependency on `muscles-data` is versioned as `>=0.1.0,<1.0.0`.

Before publishing a GitHub Release, run:

```bash
PYTHONPATH=../muscles-data/src:src python -m pytest -q
python -m build --wheel --sdist
```

The SQLite integration scenario runs without external services. PostgreSQL
coverage is enabled with `MUSCLES_DATA_INTEGRATION=1` and
`SQLALCHEMY_POSTGRES_URL`. The adapter owns engine/session lifecycle only; it
does not duplicate repositories, units of work or migrations from
`muscles-sql`.

The PyPI workflow publishes only after a GitHub Release is published. It uses
the versioned `muscles-data` dependency and trusted publishing.
