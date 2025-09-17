# Catalyst Center MCP

Catalyst Center MCP is a Python-based Model Context Protocol (MCP) server for Cisco Catalyst Center. It provides tools for querying the Catalyst Center Intent API (v2.3.7.9) to discover, monitor, and manage your Catalyst Center environment.

DISCLAIMER: THIS IS CURRENTLY BUILT FOR USE IN A DEVNET ENVIORMENT FOR POC. SSL VERIFICATION IS DISABLED. THIS IS NOT RECCOMENED FOR PRODUCTION USE.

## Features

- **Site Management**: Create and manage sites in Catalyst Center
- **Device Management**: Manage network devices and their credentials
- **Endpoint Analytics**: Manage profiling rules and fetch endpoint counts
- **Network Automation**: Support for bulk operations and asynchronous tasks
- **Advanced Monitoring**: Access network health and analytics data

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/catalyst-center-mcp.git
   cd Catalyst_Center_MCP
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:

   ```bash
   cp .env-example .env
   ```

2. Update the `.env` file with your Catalyst Center API token and base URL:

   ```env
   CATALYST_API_BASE_URL=https://your-catalyst-center/dna/intent/api/v1
   CATALYST_API_TOKEN=Your_Catalyst_Center_API_Token_here
   ```

## Usage with Claude Desktop Client

1. Configure Claude Desktop to use this MCP server:

   - Open Claude Desktop
   - Navigate to **Settings > Developer > Edit Config**
   - Add the following configuration to `claude_desktop_config.json`:

     ```json
     {
       "mcpServers": {
            "Catalyst_Center_MCP": {
              "command": "/Users/jariebel/Desktop/Catalyst_Center_MCP/.venv/bin/fastmcp",
              "args": [
                "run",
                "/path/to/Catalyst_Center_MCP/catalyst_center_mcp.py"
        ]
      }
       }
     }
     ```

   - Replace `/path/to/Catalyst_Center_MCP` with the actual path to your repository

2. Restart Claude Desktop
3. Interact with the Catalyst Center MCP via Claude Desktop

## Network Tools Guide

### Table of Contents

- [Site Management Tools](#site-management-tools)
- [Device Management Tools](#device

Replace /path/to/catalyst-center-mcp with the actual path to your repository.



Restart Claude Desktop.



Interact with the Catalyst Center MCP via Claude Desktop.

Network Tools Guide

Table of Contents





Site Management Tools



Device Management Tools



Endpoint Analytics Tools



Network Automation Tools

Site Management Tools





GET /sites - Retrieve a list of sites.



POST /sites - Create a new site in Catalyst Center.

Device Management Tools





GET /devices - Retrieve a list of network devices.



POST /device-credentials - Create device credentials.

Endpoint Analytics Tools





GET /endpoint-analytics/profiling-rules/{rule_id} - Fetch details of a profiling rule.



POST /endpoint-analytics/profiling-rules - Create a new profiling rule.



GET /endpoint-analytics/endpoints/count - Fetch the count of endpoints matching filter criteria.

Best Practices





Error Handling: Check API responses for errors.



Rate Limiting: Implement delays to respect Catalyst Center API rate limits.



Security: Keep API tokens secure and rotate them regularly.



Validation: Use provided Pydantic schemas for data validation.

Troubleshooting





Authentication Errors: Verify the API token and its permissions.



Rate Limiting: Implement delays if rate limit errors occur.



Resource Not Found: Ensure correct IDs (site, device, rule) are used.

Disclaimer

This software is provided "AS IS" without warranty. Use in production environments at your own risk. Ensure API tokens are stored securely and rotated regularly.

About

Catalyst Center MCP server for managing Cisco Catalyst Center resources via the Intent API.
