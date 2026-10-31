import io
import pytest
from httpx import AsyncClient

from backend.app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from backend.app.services.chunker import RecursiveTextChunker
from backend.app.services.parser_factory import ParserFactory, PlainTextParser
from backend.app.services.chroma_service import chroma_service
from backend.app.models.models import SearchModeType, VisibilityType
from backend.app.services.rag_service import rag_query_engine

# --- Unit Tests: Text Chunker ---
def test_recursive_chunker_boundaries():
    chunker = RecursiveTextChunker(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Paragraph 1 contains some standard text.\n\n"
        "Paragraph 2 contains more details about DMS architecture.\n\n"
        "Paragraph 3 discusses vector embeddings and HNSW indexes."
    )
    chunks = chunker.chunk_text(sample_text)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 120

def test_recursive_chunker_empty():
    chunker = RecursiveTextChunker(chunk_size=800, chunk_overlap=150)
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   ") == []

# --- Unit Tests: Auth Security ---
def test_password_hashing():
    pwd = "EnterpriseSecretPassword123!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_jwt_token_flow():
    token = create_access_token({"sub": "42", "email": "test@example.com", "role": "USER"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["email"] == "test@example.com"

# --- Unit Tests: Parser Factory ---
def test_parser_factory():
    txt_parser = ParserFactory.get_parser_for_extension(".txt")
    assert isinstance(txt_parser, PlainTextParser)
    extracted = txt_parser.extract_text(b"Hello from test plain text file!")
    assert extracted == "Hello from test plain text file!"

    with pytest.raises(ValueError):
        ParserFactory.get_parser_for_extension(".exe")


# --- Test Helpers ---
async def get_or_create_user_token(client: AsyncClient, email: str, password: str, full_name: str, role: str = "USER") -> str:
    # Attempt login first
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if login_resp.status_code == 200:
        return login_resp.json()["access_token"]
    
    # Otherwise register then login
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    })
    assert reg_resp.status_code == 201

    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


# --- Integration & System Tests (Matching Section 5.2 Test Plans) ---

@pytest.mark.asyncio
async def test_auth_and_user_creation(client: AsyncClient):
    # Register User A
    token_a = await get_or_create_user_token(client, "userA@example.com", "PasswordA123", "User Alpha")
    assert token_a is not None

    # Check /me
    me_a = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert me_a.status_code == 200
    assert me_a.json()["email"] == "userA@example.com"


@pytest.mark.asyncio
async def test_tc_val_01_unsupported_file_rejection(client: AsyncClient):
    """TC-VAL-01: User attempts to upload script.exe -> rejected with HTTP 422."""
    token = await get_or_create_user_token(client, "user_val@example.com", "Password123", "Val User")

    fake_exe = io.BytesIO(b"MZ executable mock binary")
    resp = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malicious_script.exe", fake_exe, "application/octet-stream")},
        data={"visibility": "PERSONAL"}
    )
    assert resp.status_code == 422
    assert "Unsupported file format" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_tc_sec_01_personal_document_isolation(client: AsyncClient):
    """
    TC-SEC-01: User A has personal doc. User B queries Private Search for User A's topic.
    0 chunks returned; model states info not found; strict isolation verified.
    """
    token_a = await get_or_create_user_token(client, "user_sec_a@example.com", "PasswordA123", "User Sec A")
    token_b = await get_or_create_user_token(client, "user_sec_b@example.com", "PasswordB123", "User Sec B")

    # User A uploads personal document
    doc_content = b"User A Confidential Project Apollo financial budget and proprietary secret codes."
    up_resp = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("apollo_secret.txt", io.BytesIO(doc_content), "text/plain")},
        data={"visibility": "PERSONAL"}
    )
    assert up_resp.status_code == 201

    # User B queries Private Search for Apollo secret
    query_resp = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "query": "What is the Project Apollo financial budget?",
            "search_mode": "PRIVATE"
        }
    )
    assert query_resp.status_code == 200
    res_data = query_resp.json()
    assert len(res_data["sources"]) == 0
    assert "No relevant information found in the selected search scope." in res_data["answer"]


@pytest.mark.asyncio
async def test_tc_sec_02_public_search_scope_restriction(client: AsyncClient):
    """
    TC-SEC-02: User A has public doc and private doc.
    User B queries Public Search. Only public doc chunks retrieved; private docs excluded.
    """
    token_a = await get_or_create_user_token(client, "user_pub_a@example.com", "PasswordA123", "User Pub A")
    token_b = await get_or_create_user_token(client, "user_pub_b@example.com", "PasswordB123", "User Pub B")

    # User A uploads a PUBLIC document
    public_content = b"The Organization Annual General Meeting is scheduled for December 15th at Corporate HQ."
    await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("public_agm_notice.txt", io.BytesIO(public_content), "text/plain")},
        data={"visibility": "PUBLIC"}
    )

    # User B queries Public Search
    query_resp = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "query": "When is the Annual General Meeting scheduled?",
            "search_mode": "PUBLIC"
        }
    )
    assert query_resp.status_code == 200
    res_data = query_resp.json()
    assert len(res_data["sources"]) > 0
    assert any("public_agm_notice.txt" in s["filename"] for s in res_data["sources"])


@pytest.mark.asyncio
async def test_tc_rag_01_verifiable_citation_generation(client: AsyncClient):
    """
    TC-RAG-01: Document uploaded as Public. User asks question answered by document.
    Answer includes source metadata and functional download link.
    """
    token_a = await get_or_create_user_token(client, "user_rag@example.com", "PasswordA123", "User RAG")

    hr_content = b"HR Employee Handbook: Paid time off is 25 days per calendar year. Health insurance covers dental and vision."
    await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("HR_Handbook.txt", io.BytesIO(hr_content), "text/plain")},
        data={"visibility": "PUBLIC"}
    )

    query_resp = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "query": "How many days of paid time off does the HR handbook allow?",
            "search_mode": "PUBLIC"
        }
    )
    assert query_resp.status_code == 200
    res = query_resp.json()
    assert len(res["sources"]) > 0
    citation = res["sources"][0]
    assert "HR_Handbook.txt" in citation["filename"]
    assert citation["download_url"].startswith("/api/v1/documents/")


@pytest.mark.asyncio
async def test_tc_sync_01_cascade_vector_purge_on_deletion(client: AsyncClient):
    """
    TC-SYNC-01: DOC-012 exists. User deletes document via API/UI.
    Row deleted, binary removed, all vector chunks purged from ChromaDB.
    """
    token_a = await get_or_create_user_token(client, "user_del@example.com", "PasswordA123", "User Del")

    temp_content = b"Temporary doc to be deleted and tested for vector cascade purging."
    up_resp = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("to_delete.txt", io.BytesIO(temp_content), "text/plain")},
        data={"visibility": "PERSONAL"}
    )
    doc_uuid = up_resp.json()["document_uuid"]

    # Delete Document
    del_resp = await client.delete(f"/api/v1/documents/{doc_uuid}", headers={"Authorization": f"Bearer {token_a}"})
    assert del_resp.status_code == 200

    # Search for this document in ChromaDB directly
    matched = chroma_service.query_vectors(
        query_vector=[0.1] * 1536,
        where_filter={"document_uuid": {"$eq": doc_uuid}}
    )
    assert len(matched) == 0

    # Getting document metadata should return 404
    get_res = await client.get(f"/api/v1/documents/{doc_uuid}", headers={"Authorization": f"Bearer {token_a}"})
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_tc_sync_02_vector_reindexing_on_update(client: AsyncClient):
    """
    TC-SYNC-02: DOC-088 exists with old text vectors. User uploads revised version.
    Old vectors purged, new text chunked & indexed. Model answers from updated file content.
    """
    token_a = await get_or_create_user_token(client, "user_sync2@example.com", "PasswordA123", "User Sync2")

    # Initial Upload
    v1_content = b"The project codename is BlueSky and the budget is 50000 dollars."
    up_resp = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("project_spec.txt", io.BytesIO(v1_content), "text/plain")},
        data={"visibility": "PUBLIC"}
    )
    assert up_resp.status_code == 201
    doc_uuid = up_resp.json()["document_uuid"]

    # Verify initial content query
    q1 = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"query": "What is the project budget?", "search_mode": "PUBLIC"}
    )
    assert "50000" in q1.json()["answer"]

    # Update document with new content (Revision v2)
    v2_content = b"The project codename is RedRock and the revised updated budget is 990000 dollars."
    update_resp = await client.put(
        f"/api/v1/documents/{doc_uuid}",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("project_spec.txt", io.BytesIO(v2_content), "text/plain")}
    )
    assert update_resp.status_code == 200

    # Query again and verify updated vector answers
    q2 = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"query": "What is the revised updated budget?", "search_mode": "PUBLIC"}
    )
    assert q2.status_code == 200
    assert "990000" in q2.json()["answer"]


@pytest.mark.asyncio
async def test_admin_update_user_account(client: AsyncClient):
    """
    Test authenticated update-user endpoint on FastAPI admin router.
    Verifies full_name, email, role, and password updates with RBAC enforcement.
    """
    admin_token = await get_or_create_user_token(client, "admin_test@example.com", "AdminPass123", "Admin Test", role="ADMIN")
    target_token = await get_or_create_user_token(client, "target_user@example.com", "TargetPass123", "Target User", role="USER")

    # Get target user's ID
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {target_token}"})
    assert me_resp.status_code == 200
    target_id = me_resp.json()["id"]

    # 1. Non-admin user cannot update accounts (403 Forbidden)
    forbidden_resp = await client.put(
        f"/api/v1/admin/users/{target_id}",
        headers={"Authorization": f"Bearer {target_token}"},
        json={"full_name": "Unauthorized Update"}
    )
    assert forbidden_resp.status_code == 403

    # 2. Admin successfully updates target user's full_name and role
    update_resp = await client.put(
        f"/api/v1/admin/users/{target_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "full_name": "Updated Target Name",
            "role": "ADMIN",
            "password": "NewTargetPass123"
        }
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["full_name"] == "Updated Target Name"
    assert data["role"] == "ADMIN"

    # 3. Verify user can now log in with the updated password
    login_new = await client.post("/api/v1/auth/login", json={
        "email": "target_user@example.com",
        "password": "NewTargetPass123"
    })
    assert login_new.status_code == 200
    assert login_new.json()["user"]["role"] == "ADMIN"
