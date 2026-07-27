from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from muscles_data.catalog import DataAdapterCatalog
from muscles_data.config import DataConfig
from muscles_data.contracts import assert_sql_resource_contract
from muscles_data.ports import SqlResourcePort
from muscles_data.runtime import DataRuntime

from muscles_data_sqlalchemy import SqlAlchemySqlResourceFactory


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("MUSCLES_DATA_INTEGRATION"), reason="backend integration is disabled"),
]


def _runtime(url: str) -> DataRuntime:
    config = DataConfig.from_raw(
        {
            "data": {
                "resources": {
                    "sql.integration": {
                        "type": "sqlalchemy",
                        "url": url,
                        "name": "integration_sql",
                        "pool_pre_ping": True,
                    }
                }
            }
        }
    )
    catalog = DataAdapterCatalog.with_defaults()
    catalog.register(SqlAlchemySqlResourceFactory())
    return DataRuntime(config=config, catalog=catalog)


def test_sqlalchemy_real_session_and_health_lifecycle():
    from sqlalchemy import text

    with TemporaryDirectory() as temporary:
        runtime = _runtime(f"sqlite:///{Path(temporary) / 'integration.sqlite3'}")
        try:
            sql = runtime.require_port("sql.integration", SqlResourcePort)
            with sql.session() as session:
                assert session.execute(text("select 1")).scalar_one() == 1
            assert sql.doctor()["status"] == "ok"
            assert runtime.doctor()["status"] == "ok"
            assert_sql_resource_contract(lambda: sql)
        finally:
            runtime.close()


def test_sqlalchemy_postgresql_configuration_when_driver_is_available():
    pytest.importorskip("psycopg")
    url = os.getenv("SQLALCHEMY_POSTGRES_URL")
    if not url:
        pytest.skip("PostgreSQL integration URL is not configured")
    from sqlalchemy import text

    runtime = _runtime(url)
    try:
        sql = runtime.require_port("sql.integration", SqlResourcePort)
        with sql.session() as session:
            assert session.execute(text("select 1")).scalar_one() == 1
        assert sql.doctor()["status"] == "ok"
    finally:
        runtime.close()
