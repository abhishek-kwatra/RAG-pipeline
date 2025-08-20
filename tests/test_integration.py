import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from backend.app import app  # Adjust if your app is elsewhere
from backend.services.create_test_pdf import create_test_pdf  # Helper to generate fake PDF


@pytest.mark.asyncio
async def test_upload_valid_pdf(tmp_path):
    pdf_bytes = create_test_pdf("Hello Sir I am doing an integration test")
    file = {"files": ("test.pdf", pdf_bytes, "application/pdf")}


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/upload", files=file)

    assert res.status_code == 200
    body = res.json()
    assert body["total_files"] == 1
    assert body["total_chunks"] > 0


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf():
    file = {"files": ("test.txt", b"Not a PDF", "text/plain")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/upload", files=file)

    assert res.status_code == 400
    assert "not a pdf" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_rejects_large_pdf(monkeypatch):
    import fitz  

    class FakeDoc:
        def __len__(self): return 1001
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def get_text(self): return "too big"

    monkeypatch.setattr(fitz, "open", lambda *a, **k: FakeDoc())

    pdf_bytes = create_test_pdf("Big PDF")
    file = {"files": ("big.pdf", pdf_bytes, "application/pdf")}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/upload", files=file)

    assert res.status_code == 400
    assert "more than 1000 pages" in res.json()["detail"].lower()
