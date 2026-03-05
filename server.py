import os
import httpx
from fastmcp import FastMCP

SN_URL = os.environ["SN_URL"]
SN_USER = os.environ["SN_USER"]
SN_PASS = os.environ["SN_PASS"]

mcp = FastMCP(name="ServiceNow PDI MCP")

def sn_client():
    return httpx.Client(
        base_url=f"{SN_URL}/api/now",
        auth=(SN_USER, SN_PASS),
        timeout=10.0,
    )

@mcp.tool()
def get_incident(number: str) -> dict:
    """Pobierz incident po numerze (np. INC0010001)."""
    with sn_client() as c:
        r = c.get("/table/incident", params={
            "sysparm_query": f"number={number}",
            "sysparm_limit": 1,
        })
        r.raise_for_status()
        result = r.json().get("result", [])
        return result[0] if result else {}

@mcp.tool()
def create_incident(short_description: str, description: str = "") -> dict:
    """Utwórz nowy incident w PDI."""
    with sn_client() as c:
        r = c.post("/table/incident", json={
            "short_description": short_description,
            "description": description,
        })
        r.raise_for_status()
        return r.json().get("result", {})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
