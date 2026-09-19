"""TigerGraph Database Connector & In-Memory Graph Engine.

Provides dual-mode execution:
1. Live TigerGraph Connection (via pyTigerGraph REST / GSQL endpoints).
2. Embedded In-Memory Knowledge Graph Engine for offline/local research runs.
"""

from typing import List, Dict, Any, Optional, Set
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)



class TigerGraphClient:
    def __init__(
        self,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        graph_name: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.host = host or os.getenv("TIGERGRAPH_HOST", "http://127.0.0.1:9000")
        self.username = username or os.getenv("TIGERGRAPH_USERNAME", "tigergraph")
        self.password = password or os.getenv("TIGERGRAPH_PASSWORD", "tigergraph")
        self.graph_name = graph_name or os.getenv("TIGERGRAPH_GRAPH_NAME", "olympic_qa_graph")
        self.token = token or os.getenv("TIGERGRAPH_TOKEN", "")

        self.is_connected = False
        self._conn = None

        # Embedded Graph Store: vertices { type: { id: { attributes } } }
        self.vertices: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Edges: [ { from_type, from_id, to_type, to_id, edge_type, attributes } ]
        self.edges: List[Dict[str, Any]] = []

        self._initialize_client()

    def _initialize_client(self):
        """Try connecting to live TigerGraph if reachable, otherwise initialize embedded engine."""
        try:
            import pyTigerGraph as tg
            conn = tg.TigerGraphConnection(
                host=self.host,
                username=self.username,
                password=self.password,
                graphname=self.graph_name,
            )
            if self.token:
                try:
                    conn.apiToken = self.token
                except Exception:
                    pass
                try:
                    conn.getToken(self.token)
                except Exception:
                    pass

            # Quick probe
            res = conn.getVer()
            if res:
                self._conn = conn
                self.is_connected = True
                logger.info(f"Connected to TigerGraph server version {res}")
        except Exception as e:
            logger.info(f"TigerGraph server not reachable at {self.host} ({e}). Using embedded knowledge graph engine.")
            self.is_connected = False


    def add_vertex(self, v_type: str, v_id: str, attributes: Optional[Dict[str, Any]] = None):
        if v_type not in self.vertices:
            self.vertices[v_type] = {}
        self.vertices[v_type][v_id] = attributes or {}

    def add_edge(
        self,
        from_type: str,
        from_id: str,
        to_type: str,
        to_id: str,
        edge_type: str,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.edges.append({
            "from_type": from_type,
            "from_id": from_id,
            "to_type": to_type,
            "to_id": to_id,
            "edge_type": edge_type,
            "attributes": attributes or {},
        })

    def get_schema(self) -> Dict[str, Any]:
        """Return graph schema representation."""
        if self.is_connected and self._conn:
            try:
                return self._conn.getSchema()
            except Exception as e:
                logger.warning(f"Failed to fetch live schema: {e}")

        v_types = list(self.vertices.keys())
        e_types = list(set(e["edge_type"] for e in self.edges))
        return {
            "graph_name": self.graph_name,
            "status": "LIVE_SERVER" if self.is_connected else "EMBEDDED_GRAPH_ENGINE",
            "vertex_types": v_types,
            "edge_types": e_types,
            "vertex_count": sum(len(v) for v in self.vertices.values()),
            "edge_count": len(self.edges),
        }

    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by name or attribute match."""
        q_lower = query.lower()
        results: List[Dict[str, Any]] = []
        seen_ids = set()

        for v_type, nodes in self.vertices.items():
            for v_id, attrs in nodes.items():
                name = str(attrs.get("name") or v_id)
                n_lower = name.lower()
                v_lower = v_id.lower()

                # Match if query substring in name, or entity name substring in query
                if (
                    (q_lower in n_lower or q_lower in v_lower)
                    or (len(n_lower) >= 3 and n_lower in q_lower)
                    or (len(v_lower) >= 3 and v_lower in q_lower)
                ):
                    if v_id not in seen_ids:
                        seen_ids.add(v_id)
                        results.append({
                            "vertex_type": v_type,
                            "vertex_id": v_id,
                            "name": name,
                            "attributes": attrs,
                        })
                        if len(results) >= limit:
                            return results

        return results

    def traverse(
        self,
        start_entity_id: str,
        max_hops: int = 2,
        edge_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Perform multi-hop BFS graph traversal starting from entity ID or Name."""
        resolved_id = start_entity_id
        for v_type, nodes in self.vertices.items():
            if start_entity_id in nodes:
                resolved_id = start_entity_id
                break
            for v_id, attrs in nodes.items():
                attr_name = str(attrs.get("name", "")).lower()
                s_low = start_entity_id.lower()
                v_low = v_id.lower()
                if (
                    v_low == s_low
                    or v_low == s_low.replace(" ", "_")
                    or attr_name == s_low
                    or (len(attr_name) >= 4 and attr_name in s_low)
                    or (len(s_low) >= 4 and s_low in attr_name)
                    or (len(v_low) >= 4 and v_low in s_low)
                ):
                    resolved_id = v_id
                    break

        visited_nodes: Set[str] = {resolved_id}
        frontier: List[str] = [resolved_id]
        traversed_edges: List[Dict[str, Any]] = []
        hop_records: List[Dict[str, Any]] = []

        for hop in range(1, max_hops + 1):
            next_frontier: List[str] = []
            hop_edges: List[Dict[str, Any]] = []

            for current_node in frontier:
                for edge in self.edges:
                    if edge_filter and edge["edge_type"] not in edge_filter:
                        continue

                    # Outgoing edge
                    if edge["from_id"] == current_node and edge["to_id"] not in visited_nodes:
                        visited_nodes.add(edge["to_id"])
                        next_frontier.append(edge["to_id"])
                        hop_edges.append(edge)
                    # Incoming edge (bi-directional traversal)
                    elif edge["to_id"] == current_node and edge["from_id"] not in visited_nodes:
                        visited_nodes.add(edge["from_id"])
                        next_frontier.append(edge["from_id"])
                        hop_edges.append(edge)

            traversed_edges.extend(hop_edges)
            hop_records.append({
                "hop": hop,
                "nodes_discovered": len(next_frontier),
                "edges_traversed": len(hop_edges),
            })
            frontier = next_frontier
            if not frontier:
                break

        return {
            "start_node": start_entity_id,
            "total_hops": len(hop_records),
            "visited_node_count": len(visited_nodes),
            "traversed_edge_count": len(traversed_edges),
            "edges": traversed_edges,
            "nodes": list(visited_nodes),
            "hop_breakdown": hop_records,
        }

    def execute_gsql(self, query: str) -> Dict[str, Any]:
        """Execute GSQL query or structural simulation."""
        if self.is_connected and self._conn:
            try:
                res = self._conn.gsql(query)
                return {"status": "success", "results": res}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {
            "status": "success",
            "query": query,
            "mode": "EMBEDDED_GRAPH_ENGINE",
            "result": f"Executed query across {len(self.vertices)} entity types and {len(self.edges)} relationships.",
        }


# Global singleton instance
_GLOBAL_TG_CLIENT = TigerGraphClient()


def get_tigergraph_client() -> TigerGraphClient:
    return _GLOBAL_TG_CLIENT
