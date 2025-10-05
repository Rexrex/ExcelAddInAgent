# ExcelAddInAgent

A sophisticated AI-powered assistant system built with FastAPI and Pydantic AI that provides intelligent routing between specialized agents for Excel-related tasks and general research queries.

## Overview

ExcelAddInAgent is a multi-agent AI system that intelligently routes user requests to specialized agents based on the content and context of the query. The system consists of:

- **Router Agent**: Intelligently routes requests to appropriate specialized agents
- **Excel Agent**: Expert in Microsoft Excel operations, formulas, and data analysis
- **Research Agent**: Performs web searches and gathers information using Tavily and DuckDuckGo
- **Report Generation Agent**: Creates comprehensive reports and summaries from collected data

## Architecture

```

```

## Features

### Core Functionality
- **Intelligent Request Routing**: Automatically determines whether a query requires Excel expertise or general research
- **Excel Expertise**: Provides detailed Excel instructions, formulas, and data analysis guidance
- **Deep Research**: Performs comprehensive web searches using multiple search engines
    - **Report Generation**: Creates structured reports and executive summaries
    - **Real-time Communication**: WebSocket support for interactive conversations
    - **Conversation History**: Maintains context across multiple interactions

### Technical Features
- **RESTful API**: Clean HTTP endpoints for chat interactions
- **WebSocket Support**: Real-time bidirectional communication
- **API Key Authentication**: Secure access control
- **Prompt Management**: Integration with LangFuse for prompt versioning and management

## Installation

### Prerequisites
- Python 3.8+
- API keys for external services (Tavily, LangFuse)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rexrex/ExcelAddInAgent.git
   cd ExcelAddInAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your API keys:
   ```env
   API_KEY=your_secure_api_key_here
   TAVILY_API_KEY=your_tavily_api_key
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   ```

4. **Run the application**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```