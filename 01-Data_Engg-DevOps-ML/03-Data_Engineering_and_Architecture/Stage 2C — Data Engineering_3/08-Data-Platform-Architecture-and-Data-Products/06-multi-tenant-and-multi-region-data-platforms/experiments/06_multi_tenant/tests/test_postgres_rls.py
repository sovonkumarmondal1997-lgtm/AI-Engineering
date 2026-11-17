import os
import pytest

URL_A = os.getenv("TEST_DATABASE_URL_A")
URL_B = os.getenv("TEST_DATABASE_URL_B")
if URL_A and URL_B:
    import psycopg
    from psycopg.rows import dict_row
else:
    psycopg = None
    dict_row = None
pytestmark = pytest.mark.skipif(not (URL_A and URL_B), reason="Set TEST_DATABASE_URL_A and TEST_DATABASE_URL_B to run real PostgreSQL RLS integration tests")
A = "11111111-1111-1111-1111-111111111111"
B = "22222222-2222-2222-2222-222222222222"

def connect(url):
    return psycopg.connect(url, row_factory=dict_row)

def test_tenant_a_cannot_read_update_or_spoof_tenant_b():
    with connect(URL_A) as conn:
        rows = conn.execute("SELECT tenant_id::text, event_type FROM app.events ORDER BY event_type").fetchall()
        assert rows and {row["tenant_id"] for row in rows} == {A}
        changed = conn.execute("UPDATE app.events SET event_type = 'tampered' WHERE tenant_id = %s RETURNING event_id", (B,)).fetchall()
        assert changed == []
        changed_without_tenant_filter = conn.execute("UPDATE app.events SET event_type = 'tampered' WHERE event_type = 'purchase' RETURNING event_id").fetchall()
        assert changed_without_tenant_filter == []
        deleted = conn.execute("DELETE FROM app.events WHERE tenant_id = %s RETURNING event_id", (B,)).fetchall()
        assert deleted == []
        # A shared-GUC policy would be spoofable; this policy must ignore the GUC.
        conn.execute("SELECT set_config('app.tenant_id', %s, true)", (B,))
        after_spoof = conn.execute("SELECT tenant_id::text FROM app.events").fetchall()
        assert after_spoof and {row["tenant_id"] for row in after_spoof} == {A}

def test_tenant_a_cannot_insert_tenant_b_row_and_tenant_b_sees_only_b():
    with connect(URL_A) as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with conn.transaction():
                conn.execute("INSERT INTO app.events (tenant_id, event_type) VALUES (%s, 'spoof')", (B,))
    with connect(URL_B) as conn:
        rows = conn.execute("SELECT tenant_id::text FROM app.events").fetchall()
        assert rows and {row["tenant_id"] for row in rows} == {B}
