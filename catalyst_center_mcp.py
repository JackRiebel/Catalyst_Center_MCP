import os
from typing import List, Dict, Any, Optional
import asyncio
import json
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("CATALYST_API_BASE_URL", "https://sandboxdnac.cisco.com/dna/intent/api/v1")
API_TOKEN = os.getenv("CATALYST_API_TOKEN")

if not API_TOKEN:
    raise ValueError("CATALYST_API_TOKEN environment variable is required")


HEADERS = {
    "X-Auth-Token": API_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Pydantic models for validation
class Site(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class Device(BaseModel):
    id: str
    hostname: str
    family: str
    role: str
    ip_address: Optional[str] = None

class Endpoint(BaseModel):
    mac: Optional[str] = None
    ip_address: Optional[str] = None
    username: Optional[str] = None

class DeviceDetails(BaseModel):
    hostname: str
    family: str
    software_version: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = None

class TaskResult(BaseModel):
    task_id: Optional[str] = None
    status: Optional[str] = None

# Initialize FastMCP server
mcp = FastMCP("catalyst_center_mcp")

# Helper for API calls with rate limiting and error handling
async def make_api_request(method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make an authenticated request to the Catalyst Center API with SSL verification disabled.
    """
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    try:
        # --- CHANGE MADE HERE: verify=False to disable SSL certificate verification ---
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            response = await client.request(method, url, headers=HEADERS, params=params, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication failed. Check your API token."}
        elif e.response.status_code == 429:
            await asyncio.sleep(1)  # Rate limit delay
            return {"error": "Rate limit exceeded. Please try again later."}
        else:
            return {"error": f"API error: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        print(f"DEBUG: httpx.RequestError encountered: {e}") # Keep for debugging network issues
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        print(f"DEBUG: Unexpected error encountered: {e}") # Keep for debugging unexpected errors
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def get_sites() -> str:
    """
    Retrieve a list of sites from Catalyst Center.

    Returns:
        A JSON-formatted string listing sites with ID, name, and description.
    """
    data = await make_api_request("GET", "site")
    if "error" in data:
        return json.dumps({"error": data["error"]}, indent=2)
    
    sites = [Site(id=site["id"], name=site["name"], description=site.get("description")).dict() 
             for site in data.get("response", [])]
    if not sites:
        return json.dumps({"message": "No sites found."}, indent=2)
    
    return json.dumps(sites, indent=2)

@mcp.tool()
async def get_devices(site_id: Optional[str] = None) -> str:
    """
    Retrieve devices from Catalyst Center, optionally filtered by site.

    Args:
        site_id: Optional site ID to filter devices.

    Returns:
        A JSON-formatted string listing devices with hostname, family, role, and IP.
    """
    params = {"siteId": site_id} if site_id else None
    data = await make_api_request("GET", "network-device", params=params)
    if "error" in data:
        return json.dumps({"error": data["error"]}, indent=2)
    
    devices = [Device(id=dev["id"], hostname=dev["hostname"], family=dev["family"], 
                      role=dev["role"], ip_address=dev.get("managementIpAddress")).dict() 
               for dev in data.get("response", [])]
    if not devices:
        return json.dumps({"message": "No devices found."}, indent=2)
    
    return json.dumps(devices, indent=2)

@mcp.tool()
async def get_endpoints(device_id: str) -> str:
    """
    Retrieve endpoints (clients) for a specific device.

    Args:
        device_id: The ID of the device to query endpoints for.

    Returns:
        A JSON-formatted string listing endpoints with MAC, IP, and username.
    """
    data = await make_api_request("GET", f"device/{device_id}/endpoint")
    if "error" in data:
        return json.dumps({"error": data["error"]}, indent=2)
    
    endpoints = [Endpoint(mac=ep.get("mac"), ip_address=ep.get("ipAddress"), username=ep.get("username")).dict() 
                 for ep in data.get("response", [])]
    if not endpoints:
        return json.dumps({"message": "No endpoints found for this device."}, indent=2)
    
    return json.dumps(endpoints, indent=2)

@mcp.tool()
async def get_device_details(device_id: str) -> str:
    """
    Get detailed information for a specific device.

    Args:
        device_id: The ID of the device.

    Returns:
        A JSON-formatted string with device details (hostname, family, software version, serial number, status).
    """
    data = await make_api_request("GET", f"network-device/{device_id}")
    if "error" in data:
        return json.dumps({"error": data["error"]}, indent=2)
    
    device = data.get("response", {})
    details = DeviceDetails(
        hostname=device.get("hostname", "N/A"),
        family=device.get("family", "N/A"),
        software_version=device.get("softwareVersion"),
        serial_number=device.get("serialNumber"),
        status=device.get("reachabilityStatus")
    ).dict()
    return json.dumps(details, indent=2)

@mcp.tool()
async def run_automation_task(task_type: str, params: Dict[str, Any]) -> str:
    """
    Run a network automation task (e.g., provision device, update config).

    Args:
        task_type: Type of task (e.g., 'provision_device', 'update_config').
        params: Dictionary of task parameters (e.g., {'device_id': 'abc', 'config': '...'})

    Returns:
        A JSON-formatted string with task execution result or status.
    """
    data = await make_api_request("POST", "task", data={"taskType": task_type, "params": params})
    if "error" in data:
        return json.dumps({"error": data["error"]}, indent=2)
    
    result = TaskResult(task_id=data.get("taskId"), status=data.get("progress")).dict()
    return json.dumps({
        "status": "success",
        "task_id": result["task_id"],
        "progress": result["status"]
    }, indent=2)

@mcp.resource("greeting: //{name}")
def greeting(name: str) -> str:
    """
    Greet a user by name.

    Args:
        name: The name to include in the greeting.

    Returns:
        A greeting message.
    """
    return f"Hello {name}!"

if __name__ == "__main__":
    mcp.run(transport="stdio") # Use stdio for Claude Desktop integration
    uvicorn.run(app, host="0.0.0.0", port=8000)
