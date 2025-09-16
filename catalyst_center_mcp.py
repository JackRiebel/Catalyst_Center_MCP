import requests
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Catalyst Center API configuration
CATALYST_API_BASE_URL = os.getenv("CATALYST_API_BASE_URL", "https://your-catalyst-center/dna/intent/api/v1")
CATALYST_API_TOKEN = os.getenv("CATALYST_API_TOKEN")

if not CATALYST_API_TOKEN:
    raise ValueError("CATALYST_API_TOKEN must be set in .env file")

# Initialize FastAPI
app = FastAPI(title="Catalyst Center MCP", description="Model Context Protocol server for Cisco Catalyst Center")

# Pydantic Schemas for Data Validation
class SiteCreateSchema(BaseModel):
    siteNameHierarchy: str = Field(..., description="Full path of the site hierarchy")
    siteType: str = Field(default="FABRIC_SITE", description="Type of SD-Access Fabric, e.g., FABRIC_SITE or FABRIC_ZONE")

class DeviceCredentialSchema(BaseModel):
    description: str = Field(..., description="Description for CLI credential")
    username: str = Field(..., description="Username for CLI credential")
    password: str = Field(..., description="Password for CLI credential")
    enablePassword: Optional[str] = Field(None, description="Enable password for CLI credential")

class ProfilingRuleSchema(BaseModel):
    ruleId: str = Field(..., description="Unique rule identifier")
    ruleType: str = Field(default="Custom Rule", description="Type of profiling rule")
    # Add additional fields as needed for rule creation

class EndpointFilterSchema(BaseModel):
    profilingStatus: Optional[str] = Field(None, description="Profiling status: profiled, partialProfiled, notProfiled")
    macAddress: Optional[str] = Field(None, description="MAC address to search for")
    ip: Optional[str] = Field(None, description="IP address to search for")
    deviceType: Optional[str] = Field(None, description="Type of device to search for")

# Helper function for API requests
def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    headers = {
        "X-Auth-Token": CATALYST_API_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    url = f"{CATALYST_API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, json=data, params=params)
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

# Site Management Endpoints
@app.get("/sites", summary="Get list of sites")
async def get_sites():
    """Retrieve a list of sites from Catalyst Center."""
    try:
        response = make_api_request("GET", "/site")
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching sites: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/sites", summary="Create a new site")
async def create_site(site: SiteCreateSchema):
    """Create a new site in Catalyst Center."""
    try:
        data = {
            "siteNameHierarchy": site.siteNameHierarchy,
            "siteType": site.siteType
        }
        response = make_api_request("POST", "/site", data=[data])
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating site: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Device Management Endpoints
@app.get("/devices", summary="Get list of devices")
async def get_devices():
    """Retrieve a list of devices from Catalyst Center."""
    try:
        response = make_api_request("GET", "/network-device")
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/device-credentials", summary="Create device credentials")
async def create_device_credentials(credential: DeviceCredentialSchema):
    """Create device credentials in Catalyst Center."""
    try:
        data = {
            "settings": {
                "cliCredential": [{
                    "description": credential.description,
                    "username": credential.username,
                    "password": credential.password,
                    "enablePassword": credential.enablePassword
                }]
            }
        }
        response = make_api_request("POST", "/device-credential", data=data)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating device credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint Analytics Endpoints
@app.get("/endpoint-analytics/profiling-rules/{rule_id}", summary="Get details of a single profiling rule")
async def get_profiling_rule(rule_id: str):
    """Fetch details of a profiling rule by ruleId."""
    try:
        response = make_api_request("GET", f"/endpoint-analytics/profiling-rules/{rule_id}")
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching profiling rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/endpoint-analytics/profiling-rules", summary="Create a profiling rule")
async def create_profiling_rule(rule: ProfilingRuleSchema):
    """Create a new profiling rule in Catalyst Center."""
    try:
        data = rule.dict(exclude_unset=True)
        response = make_api_request("POST", "/endpoint-analytics/profiling-rules", data=data)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating profiling rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/endpoint-analytics/endpoints/count", summary="Fetch count of endpoints")
async def get_endpoints_count(filters: EndpointFilterSchema):
    """Fetch the total count of endpoints matching the filter criteria."""
    try:
        params = filters.dict(exclude_unset=True)
        response = make_api_request("GET", "/endpoint-analytics/endpoints/count", params=params)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching endpoints count: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)