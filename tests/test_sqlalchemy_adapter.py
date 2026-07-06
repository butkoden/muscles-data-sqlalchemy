from __future__ import annotations

import pytest
from muscles_data.catalog import DataAdapterCatalog
from muscles_data.config import DataConfig
from muscles_data.models import DataCapability
from muscles_data.ports import SqlResourcePort
from muscles_data.runtime import DataRuntime

from muscles_data_sqlalchemy import (
    SqlAlchemyClientMissingError,
    SqlAlchemyConnectionError,
    SqlAlchemySqlResourceFactory,
)


def _config(url: str = "sqlite:///:memory:") -> dict:
    return {
        "data": {
            "resources": {
                "sql.local": {
                    "type": "sqlalchemy",
                    "url": url,
                    "name": "local_sqlite",
                    "native_client": True,
                }
            }
        }
    }


def _runtime(factory: SqlAlchemySqlResourceFactory | None = None, url: str = "sqlite:///:memory:") -> DataRuntime:
    catalog = DataAdapterCatalog.with_defaults()
    catalog.register(factory or SqlAlchemySqlResourceFactory())
    return DataRuntime(config=DataConfig.from_raw(_config(url)), catalog=catalog)


def test_sqlalchemy_resource_port_is_external_lazy_and_exposes_sessions():
    sqlalchemy = pytest.importorskip("sqlalchemy")
    runtime = _runtime()

    listed = runtime.list_resources()[0]
    inspected_before = runtime.inspect_resource("sql.local")

    assert listed["type"] == "sqlalchemy"
    assert "sql_session" in listed["capabilities"]
    assert "native_client" not in listed["capabilities"]
    assert listed["initialized"] is False
    assert inspected_before["initialized"] is False
    assert inspected_before["options"]["url"] == "***"

    sql = runtime.require_port("sql.local", SqlResourcePort)
    with sql.session() as session:
        session.execute(sqlalchemy.text("create table notes (id integer primary key, title varchar)"))
        session.execute(sqlalchemy.text("insert into notes (title) values ('typed port')"))
        rows = session.execute(sqlalchemy.text("select title from notes")).fetchall()
        session.commit()

    native = runtime.require_resource("sql.local", DataCapability.NATIVE_CLIENT).native_client()
    assert [row[0] for row in rows] == ["typed port"]
    assert {"engine", "session_factory"} <= set(native)
    assert sql.inspect()["details"]["backend"] == "sqlalchemy"
    assert sql.doctor()["status"] == "ok"
    assert runtime.close()["status"] == "ok"


def test_sqlalchemy_safe_failures_and_missing_client():
    runtime = _runtime(url="missingdialect://user:secret@localhost/app")

    assert runtime.inspect_resource("sql.local")["options"]["url"] == "***"
    doctor = runtime.doctor()
    assert doctor["status"] == "failed"
    assert "secret" not in repr(doctor)

    with pytest.raises(SqlAlchemyConnectionError):
        runtime.require_port("sql.local", SqlResourcePort).session()

    missing = _runtime(SqlAlchemySqlResourceFactory(sqlalchemy_provider=lambda: None))
    with pytest.raises(SqlAlchemyClientMissingError):
        missing.require_port("sql.local", SqlResourcePort).session()
