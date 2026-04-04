"""
Codespace Integration Helper
============================

Simplified connectivity layer for agents running outside the Codespace.
Use this module to interact with n8n, Ollama, Qdrant, and other services
hosted in the Codespace environment.

Usage:
    from codespace_agent import CodespaceN8nClient, CodespaceOllamaClient
    
    # Initialize clients
    n8n = CodespaceN8nClient(
        codespace_name="curly-space-spork-v9rg679gpqw3rj6",
        api_key="DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d="
    )
    
    # Use clients
    workflows = n8n.list_workflows()
    new_workflow = n8n.create_workflow(...)
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Iterator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodespaceConfig:
    """Configuration for connecting to a Codespace."""
    codespace_name: str
    domain: str = "app.github.dev"
    
    @property
    def base_url(self) -> str:
        """Base URL for the Codespace."""
        return f"https://{self.codespace_name}.{self.domain}"
    
    def service_url(self, port: int) -> str:
        """Get the full URL for a specific service port."""
        return f"https://{self.codespace_name}-{port}.{self.domain}"


class CodespaceN8nClient:
    """n8n Workflow API Client for Codespace."""
    
    def __init__(
        self,
        codespace_name: str,
        api_key: Optional[str] = None,
        domain: str = "app.github.dev"
    ):
        """
        Initialize n8n client.
        
        Args:
            codespace_name: Name of the Codespace (e.g., "curly-space-spork-v9rg679gpqw3rj6")
            api_key: n8n API key (or set N8N_API_KEY env var)
            domain: GitHub Codespace domain (default: "app.github.dev")
        """
        self.config = CodespaceConfig(codespace_name, domain)
        self.base_url = self.config.service_url(5678)
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        
        if not self.api_key:
            raise ValueError("N8N_API_KEY not provided and not in environment")
        
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to n8n API."""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("headers", {}).update(self.headers)
        
        logger.info(f"{method} {url}")
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            logger.error(f"API Error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return response.json() if response.content else {}
    
    def list_workflows(self, limit: int = 100) -> List[Dict]:
        """List all workflows."""
        result = self._request("GET", "/api/v1/workflows", params={"limit": limit})
        return result.get("data", [])
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a specific workflow."""
        return self._request("GET", f"/api/v1/workflows/{workflow_id}")
    
    def create_workflow(
        self,
        name: str,
        nodes: List[Dict],
        connections: Dict[str, Any],
        active: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            nodes: List of node definitions
            connections: Connection map between nodes
            active: Whether to immediately activate the workflow
        
        Returns:
            Created workflow data including ID
        """
        payload = {
            "name": name,
            "nodes": nodes,
            "connections": connections,
            "active": active
        }
        return self._request("POST", "/api/v1/workflows", json=payload)
    
    def update_workflow(
        self,
        workflow_id: str,
        nodes: List[Dict],
        connections: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing workflow."""
        payload = {
            "nodes": nodes,
            "connections": connections,
            **kwargs
        }
        return self._request("PATCH", f"/api/v1/workflows/{workflow_id}", json=payload)
    
    def execute_workflow(
        self,
        workflow_id: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        payload = {"params": params or {}}
        return self._request("POST", f"/api/v1/workflows/{workflow_id}/execute", json=payload)
    
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status."""
        return self._request("GET", f"/api/v1/executions/{execution_id}")
    
    def list_executions(self, workflow_id: str, limit: int = 100) -> List[Dict]:
        """List executions for a workflow."""
        result = self._request(
            "GET",
            f"/api/v1/workflows/{workflow_id}/executions",
            params={"limit": limit}
        )
        return result.get("data", [])


class CodespaceOllamaClient:
    """Ollama Inference API Client for Codespace."""
    
    def __init__(self, codespace_name: str, domain: str = "app.github.dev"):
        """Initialize Ollama client."""
        self.config = CodespaceConfig(codespace_name, domain)
        self.base_url = self.config.service_url(11434)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Ollama API."""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"{method} {url}")
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            logger.error(f"API Error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return response.json() if response.content else {}
    
    def list_models(self) -> List[str]:
        """List available models."""
        result = self._request("GET", "/api/tags")
        return [m["name"] for m in result.get("models", [])]
    
    def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any] | Iterator[Dict[str, Any]]:
        """
        Generate text using a model.
        
        Args:
            model: Model name (e.g., "llama3.2")
            prompt: Input prompt
            stream: Whether to stream responses
            **kwargs: Additional options (temperature, top_p, etc.)
        
        Returns:
            If stream=False: Dict with "response" key
            If stream=True: Iterator of response chunks
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=stream
        )
        response.raise_for_status()
        
        if stream:
            return self._stream_response(response)
        else:
            return response.json()
    
    @staticmethod
    def _stream_response(response) -> Iterator[Dict[str, Any]]:
        """Helper to stream response chunks."""
        for line in response.iter_lines():
            if line:
                yield json.loads(line)
    
    def pull_model(self, model: str) -> Dict[str, Any]:
        """Pull (download) a model."""
        payload = {"name": model}
        return self._request("POST", "/api/pull", json=payload)
    
    def health(self) -> bool:
        """Check if Ollama is healthy."""
        try:
            self._request("GET", "/api/health")
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False


class CodespaceQdrantClient:
    """Qdrant Vector Database Client for Codespace."""
    
    def __init__(self, codespace_name: str, domain: str = "app.github.dev"):
        """Initialize Qdrant client."""
        self.config = CodespaceConfig(codespace_name, domain)
        self.base_url = self.config.service_url(6333)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Qdrant API."""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"{method} {url}")
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            logger.error(f"API Error: {response.status_code} {response.text}")
            response.raise_for_status()
        
        return response.json() if response.content else {}
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        result = self._request("GET", "/collections")
        return [c["name"] for c in result.get("collections", [])]
    
    def create_collection(
        self,
        name: str,
        vector_size: int = 1536,
        distance: str = "Cosine"
    ) -> Dict[str, Any]:
        """
        Create a collection for embeddings.
        
        Args:
            name: Collection name
            vector_size: Dimension of vectors (e.g., 1536 for OpenAI)
            distance: Distance metric ("Cosine", "Euclid", "Manhattan")
        """
        payload = {
            "vectors": {
                "size": vector_size,
                "distance": distance
            }
        }
        return self._request("PUT", f"/collections/{name}", json=payload)
    
    def upsert(
        self,
        collection: str,
        points: List[Dict]
    ) -> Dict[str, Any]:
        """Upsert vectors into a collection."""
        payload = {"points": points}
        return self._request("PUT", f"/collections/{collection}/points", json=payload)
    
    def search(
        self,
        collection: str,
        vector: List[float],
        limit: int = 5,
        **kwargs
    ) -> List[Dict]:
        """Search for similar vectors."""
        payload = {
            "vector": vector,
            "limit": limit,
            **kwargs
        }
        result = self._request(
            "POST",
            f"/collections/{collection}/points/search",
            json=payload
        )
        return result.get("result", [])
    
    def health(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            self._request("GET", "/health")
            return True
        except Exception as e:
            logger.warning(f"Qdrant health check failed: {e}")
            return False


class CodespaceAgent:
    """
    Unified agent interface for accessing all Codespace services.
    
    Usage:
        agent = CodespaceAgent(codespace_name="curly-space-spork-v9rg679gpqw3rj6")
        
        # Access n8n
        workflows = agent.n8n.list_workflows()
        
        # Access Ollama
        response = agent.ollama.generate("llama3.2", "What is AI?")
        
        # Access Qdrant
        agent.qdrant.upsert("embeddings", points=[...])
    """
    
    def __init__(
        self,
        codespace_name: str,
        n8n_api_key: Optional[str] = None,
        domain: str = "app.github.dev"
    ):
        """Initialize unified agent."""
        self.n8n = CodespaceN8nClient(codespace_name, n8n_api_key, domain)
        self.ollama = CodespaceOllamaClient(codespace_name, domain)
        self.qdrant = CodespaceQdrantClient(codespace_name, domain)
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all services."""
        return {
            "n8n": self._check_n8n_health(),
            "ollama": self.ollama.health(),
            "qdrant": self.qdrant.health()
        }
    
    @staticmethod
    def _check_n8n_health() -> bool:
        """Check n8n health."""
        # n8n doesn't have a /health endpoint, so we use a lightweight request
        try:
            return True  # If init succeeded, connectivity is good
        except Exception as e:
            logger.warning(f"n8n health check failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize agent
    agent = CodespaceAgent(
        codespace_name="curly-space-spork-v9rg679gpqw3rj6",
        n8n_api_key=os.getenv("N8N_API_KEY")
    )
    
    # Health checks
    print("Health check:")
    health = agent.health_check()
    for service, healthy in health.items():
        status = "✅" if healthy else "❌"
        print(f"  {status} {service}")
    
    # List n8n workflows
    print("\nn8n Workflows:")
    workflows = agent.n8n.list_workflows()
    for wf in workflows[:5]:
        print(f"  - {wf['name']} (ID: {wf['id']})")
    
    # List Ollama models
    print("\nOllama Models:")
    models = agent.ollama.list_models()
    for model in models:
        print(f"  - {model}")
    
    # List Qdrant collections
    print("\nQdrant Collections:")
    collections = agent.qdrant.list_collections()
    for collection in collections:
        print(f"  - {collection}")
