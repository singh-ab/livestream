import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_overlay_crud_cycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # create
        payload = {"kind":"text","content":"Hello","x":10,"y":20,"opacity":0.8}
        r = await ac.post("/api/overlays", json=payload)
        assert r.status_code == 200, r.text
        created = r.json()
        oid = created["id"]

        # list
        r = await ac.get("/api/overlays")
        assert r.status_code == 200
        assert any(o["id"] == oid for o in r.json())

        # get
        r = await ac.get(f"/api/overlays/{oid}")
        assert r.status_code == 200

        # update
        upd = payload | {"content": "World"}
        r = await ac.put(f"/api/overlays/{oid}", json=upd)
        assert r.status_code == 200
        assert r.json()["content"] == "World"

        # delete
        r = await ac.delete(f"/api/overlays/{oid}")
        assert r.status_code == 200

        # get 404
        r = await ac.get(f"/api/overlays/{oid}")
        assert r.status_code == 404
