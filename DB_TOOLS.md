# MCP Database Tools Documentation

This document describes the available MCP (Model Context Protocol) database tools for agents in the Rekindle system. These tools provide safe, read-only access to database operations with intention-revealing function names.

## Overview

The MCP database tools are implemented in `backend/crewai_agents/tools/mcp_db_tools.py` and provide agents with controlled access to database queries. All operations are read-only and scoped to prevent data leakage.

## Available Tools

### `get_pipeline_summary(account_id)`

**Parameters:**
- `account_id` (str): The unique identifier for the account

**Return Value:**
- `Dict[str, Any]`: Comprehensive pipeline metrics including:
  - Total leads in pipeline
  - Conversion rates by stage
  - Revenue projections
  - Activity metrics

**Intended Use Cases:**
- Analyzing overall sales pipeline health
- Generating performance reports
- Forecasting revenue based on current pipeline
- Identifying bottlenecks in the sales process

**Recommended Agents:**
- Analytics agents (for reporting and insights)
- Revenue agents (for forecasting and optimization)
- Master intelligence agent (for comprehensive account analysis)

### `get_campaign_performance(campaign_id)`

**Parameters:**
- `campaign_id` (str): The unique identifier for the campaign

**Return Value:**
- `Dict[str, Any]`: Detailed campaign metrics including:
  - Open rates, click rates, conversion rates
  - Revenue attribution
  - Lead quality scores
  - Timeline performance data

**Intended Use Cases:**
- Evaluating campaign effectiveness
- Optimizing campaign strategies
- Measuring ROI on marketing spend
- Identifying high-performing campaign elements

**Recommended Agents:**
- Analytics agents (for performance analysis)
- Optimization agents (for campaign improvement)
- Content agents (for content strategy refinement)

### `get_dormant_leads(account_id, since)`

**Parameters:**
- `account_id` (str): The unique identifier for the account
- `since` (datetime): The cutoff date for determining dormancy

**Return Value:**
- `List[Dict[str, Any]]`: List of dormant lead profiles including:
  - Lead contact information
  - Last activity timestamps
  - Lead quality scores
  - Previous engagement history

**Intended Use Cases:**
- Identifying leads requiring reactivation
- Prioritizing follow-up activities
- Analyzing lead engagement patterns
- Creating targeted reactivation campaigns

**Recommended Agents:**
- Dead lead reactivation agent (primary use case)
- Outreach agents (for follow-up campaigns)
- Personalizer agents (for customized reactivation messaging)

### `get_meeting_stats(account_id, period)`

**Parameters:**
- `account_id` (str): The unique identifier for the account
- `period` (str, optional): Time period for statistics (default: "30d")
  - Supported formats: "7d", "30d", "90d", "1y"

**Return Value:**
- `Dict[str, Any]`: Meeting statistics including:
  - Total meetings booked
  - Meeting types distribution
  - Conversion rates from meetings
  - Revenue generated from meetings

**Intended Use Cases:**
- Tracking sales meeting effectiveness
- Analyzing meeting-to-conversion ratios
- Optimizing meeting scheduling strategies
- Forecasting revenue from meeting pipeline

**Recommended Agents:**
- Analytics agents (for performance tracking)
- Revenue agents (for conversion analysis)
- Optimization agents (for process improvement)

## Usage Notes

- All tools require MCP server availability and will raise `RuntimeError` if the server is not accessible
- Tools are read-only and cannot modify database state
- Access is scoped to prevent data leakage between accounts
- Functions use intention-revealing names to clearly communicate their purpose

## Singleton Access

Tools are accessed via a singleton instance:

```python
from backend.crewai_agents.tools.mcp_db_tools import get_mcp_db_tools

db_tools = get_mcp_db_tools()
summary = db_tools.get_pipeline_summary(account_id)