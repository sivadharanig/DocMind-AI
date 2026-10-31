import requests
from typing import Optional, Dict, Any, List

class BackendClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_v1 = f"{self.base_url}/api/v1"

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # --- Auth Endpoints ---
    def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/auth/login"
        resp = requests.post(url, json={"email": email, "password": password})
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Login failed")}

    def register(self, email: str, password: str, full_name: str, role: str = "USER") -> Dict[str, Any]:
        url = f"{self.api_v1}/auth/register"
        resp = requests.post(url, json={"email": email, "password": password, "full_name": full_name, "role": role})
        if resp.status_code == 201:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Registration failed")}

    def get_me(self, token: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/auth/me"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}

    # --- Document Endpoints ---
    def list_documents(
        self,
        token: str,
        scope: str = "all",
        search: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.api_v1}/documents/"
        params = {"scope": scope}
        if search:
            params["search"] = search
        if file_type:
            params["file_type"] = file_type
        resp = requests.get(url, headers=self._headers(token), params=params)
        if resp.status_code == 200:
            return resp.json()
        return []

    def upload_document(self, token: str, file_name: str, file_bytes: bytes, visibility: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/documents/upload"
        files = {"file": (file_name, file_bytes)}
        data = {"visibility": visibility}
        resp = requests.post(url, headers=self._headers(token), files=files, data=data)
        if resp.status_code == 201:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Upload failed")}

    def download_document(self, token: str, document_uuid: str) -> Optional[bytes]:
        url = f"{self.api_v1}/documents/{document_uuid}/download"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return resp.content
        return None

    def update_document(
        self,
        token: str,
        document_uuid: str,
        visibility: Optional[str] = None,
        replacement_file: Optional[tuple] = None
    ) -> Dict[str, Any]:
        url = f"{self.api_v1}/documents/{document_uuid}"
        data = {}
        if visibility:
            data["visibility"] = visibility
        files = {}
        if replacement_file:
            files["file"] = replacement_file
        resp = requests.put(url, headers=self._headers(token), data=data, files=files if files else None)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Update failed")}

    def delete_document(self, token: str, document_uuid: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/documents/{document_uuid}"
        resp = requests.delete(url, headers=self._headers(token))
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Delete failed")}

    # --- Chat & RAG Endpoints ---
    def create_chat_session(self, token: str, search_mode: str = "PRIVATE") -> Dict[str, Any]:
        url = f"{self.api_v1}/chat/sessions"
        resp = requests.post(url, headers=self._headers(token), params={"search_mode": search_mode})
        if resp.status_code == 201:
            return resp.json()
        return {}

    def list_chat_sessions(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.api_v1}/chat/sessions"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return resp.json()
        return []

    def get_chat_session(self, token: str, session_uuid: str) -> Optional[Dict[str, Any]]:
        url = f"{self.api_v1}/chat/sessions/{session_uuid}"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return resp.json()
        return None

    def query_rag_chat(
        self,
        token: str,
        query: str,
        search_mode: str = "PRIVATE",
        session_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{self.api_v1}/chat/query"
        payload = {
            "query": query,
            "search_mode": search_mode,
            "session_uuid": session_uuid
        }
        resp = requests.post(url, headers=self._headers(token), json=payload)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Query failed")}

    # --- Admin Endpoints ---
    def get_admin_stats(self, token: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/admin/stats"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return resp.json()
        return {}

    def get_admin_users_overview(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.api_v1}/admin/users-overview"
        resp = requests.get(url, headers=self._headers(token))
        if resp.status_code == 200:
            return resp.json()
        return []

    def delete_user(self, token: str, user_id: int) -> Dict[str, Any]:
        url = f"{self.api_v1}/admin/users/{user_id}"
        resp = requests.delete(url, headers=self._headers(token))
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.json().get("detail", "Delete failed")}

    def update_user(
        self,
        token: str,
        user_id: int,
        *args,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.api_v1}/admin/users/{user_id}"
        payload = {}
        if args and isinstance(args[0], dict):
            payload.update(args[0])
        if full_name is not None:
            payload["full_name"] = full_name
        if email is not None:
            payload["email"] = email
        if role is not None:
            payload["role"] = role
        if password is not None:
            payload["password"] = password
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v

        try:
            resp = requests.put(url, headers=self._headers(token), json=payload)
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            err_msg = "Update failed"
            try:
                err_msg = resp.json().get("detail", err_msg)
            except Exception:
                pass
            return {"success": False, "error": err_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}

    update_admin_user = update_user
    edit_user = update_user

    def get_ai_status(self, token: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/admin/ai-status"
        try:
            resp = requests.get(url, headers=self._headers(token), timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e), "has_key": False}
        return {"status": "unknown", "message": "Failed to fetch status", "has_key": False}

    def update_ai_key(self, token: str, api_key: str) -> Dict[str, Any]:
        url = f"{self.api_v1}/admin/update-ai-key"
        try:
            resp = requests.post(url, headers=self._headers(token), json={"api_key": api_key}, timeout=10)
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            return {"success": False, "error": resp.json().get("detail", "Update failed")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/", timeout=2)
            if resp.status_code == 200:
                return {"online": True, "data": resp.json()}
        except Exception:
            pass
        return {"online": False}

backend_client = BackendClient()
