#!/usr/bin/env python3
"""
Notion PM Infrastructure as Code - SportsAnalytics Project
===========================================================

This script deploys a complete Project Management system in Notion following
the "One Truth" architecture:
    - Epics DB: High-level goals (Ingesta, Transformación, Visualización)
    - Sprints DB: Time-boxed iterations
    - Tasks DB: Granular work items with relations to Epics and Sprints

Usage:
    1. Ensure NOTION_TOKEN and NOTION_PAGE_ID are set in .env
    2. Run: python NotionIntegration/setup_pm.py

Based on recommendations from Notion-PM.md and notion-dev.md
"""

import os
import sys
import time
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

# Use explicit API version for compatibility
NOTION_API_VERSION = "2022-06-28"


def get_headers():
    """Get headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json"
    }


def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not NOTION_TOKEN or NOTION_TOKEN == "your_secret_token_here":
        errors.append(
            "NOTION_TOKEN not configured. Please update .env with your integration token.\n"
            "Get it from: https://www.notion.so/my-integrations"
        )
    
    if not NOTION_PAGE_ID:
        errors.append("NOTION_PAGE_ID not configured in .env")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nSetup instructions:")
        print("  1. Go to https://www.notion.so/my-integrations")
        print("  2. Create a new internal integration")
        print("  3. Copy the token to .env file")
        print("  4. Connect the integration to your Notion page")
        sys.exit(1)


def create_database(parent_id: str, title: str, properties: dict, icon: str = None) -> str:
    """Create a database in Notion using raw HTTP API."""
    print(f"  Creating database: {title}...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }
    
    if icon:
        payload["icon"] = {"type": "emoji", "emoji": icon}
    
    response = httpx.post(
        "https://api.notion.com/v1/databases",
        headers=get_headers(),
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        db_id = response.json()["id"]
        print(f"  Created: {title} (ID: {db_id})")
        return db_id
    else:
        error = response.json().get("message", response.text)
        print(f"  ERROR creating {title}: {error}")
        raise Exception(f"Failed to create database: {error}")


def update_database(db_id: str, properties: dict):
    """Update a database to add new properties."""
    response = httpx.patch(
        f"https://api.notion.com/v1/databases/{db_id}",
        headers=get_headers(),
        json={"properties": properties},
        timeout=30
    )
    
    if response.status_code != 200:
        error = response.json().get("message", response.text)
        raise Exception(f"Failed to update database: {error}")


def create_page(database_id: str, properties: dict) -> str:
    """Create a page (entry) in a database."""
    response = httpx.post(
        "https://api.notion.com/v1/pages",
        headers=get_headers(),
        json={
            "parent": {"database_id": database_id},
            "properties": properties
        },
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        error = response.json().get("message", response.text)
        raise Exception(f"Failed to create page: {error}")


def setup_epics_db(parent_id: str) -> str:
    """Create the Epics database."""
    # Create with just Name first
    schema = {"Name": {"title": {}}}
    db_id = create_database(parent_id, "DB Epics", schema, "🎯")
    
    # Add remaining properties
    extra_props = {
        "Description": {"rich_text": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Backlog", "color": "gray"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "Progress": {"number": {"format": "percent"}}
    }
    update_database(db_id, extra_props)
    
    return db_id


def setup_sprints_db(parent_id: str) -> str:
    """Create the Sprints database."""
    schema = {"Name": {"title": {}}}
    db_id = create_database(parent_id, "DB Sprints", schema, "🏃")
    
    extra_props = {
        "Dates": {"date": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Planning", "color": "gray"},
                    {"name": "Active", "color": "red"},
                    {"name": "Completed", "color": "green"}
                ]
            }
        },
        "Goal": {"rich_text": {}},
        "Velocity": {"number": {"format": "number"}}
    }
    update_database(db_id, extra_props)
    
    return db_id


def setup_tasks_db(parent_id: str, epics_db_id: str, sprints_db_id: str) -> str:
    """Create the Tasks database with relations."""
    schema = {"Name": {"title": {}}}
    db_id = create_database(parent_id, "DB Tasks (Master Backlog)", schema, "✅")
    
    extra_props = {
        "Status": {"status": {}},
        "Type": {
            "select": {
                "options": [
                    {"name": "Feature", "color": "blue"},
                    {"name": "Bug", "color": "red"},
                    {"name": "Research", "color": "purple"},
                    {"name": "Documentation", "color": "yellow"},
                    {"name": "Refactor", "color": "orange"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "Critical", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "Effort": {
            "select": {
                "options": [
                    {"name": "XS (< 1h)", "color": "green"},
                    {"name": "S (1-2h)", "color": "blue"},
                    {"name": "M (3-5h)", "color": "yellow"},
                    {"name": "L (1-2d)", "color": "orange"},
                    {"name": "XL (> 2d)", "color": "red"}
                ]
            }
        },
        "Epic": {
            "relation": {
                "database_id": epics_db_id,
                "type": "dual_property",
                "dual_property": {}
            }
        },
        "Sprint": {
            "relation": {
                "database_id": sprints_db_id,
                "type": "dual_property",
                "dual_property": {}
            }
        },
        "Notes": {"rich_text": {}},
        "Due Date": {"date": {}}
    }
    update_database(db_id, extra_props)
    
    return db_id


def seed_initial_data(epics_db_id: str, sprints_db_id: str, tasks_db_id: str):
    """Seed the databases with initial data for the SportsAnalytics project."""
    print("\n📦 Seeding initial data...")
    
    # Create Epics
    epics = [
        ("Epic A: Ingesta de Datos", "Configurar pipelines de extracción de datos desde APIs deportivas", "In Progress", "High"),
        ("Epic B: Transformación de Datos", "Implementar modelos dbt para transformar datos crudos", "Backlog", "High"),
        ("Epic C: Visualización y Predicciones", "Crear dashboards y modelos ML para análisis predictivo", "Backlog", "Medium")
    ]
    
    epic_ids = {}
    for name, desc, status, priority in epics:
        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Description": {"rich_text": [{"text": {"content": desc}}]},
            "Status": {"select": {"name": status}},
            "Priority": {"select": {"name": priority}},
            "Progress": {"number": 0}
        }
        epic_ids[name] = create_page(epics_db_id, props)
        print(f"    ✅ {name}")
    
    # Create Sprints
    today = datetime.now()
    sprints = [
        ("Sprint 1: Setup & Ingesta Inicial", today, today + timedelta(days=14), "Active", "Configurar infraestructura base"),
        ("Sprint 2: Transformaciones dbt", today + timedelta(days=14), today + timedelta(days=28), "Planning", "Implementar modelos de staging"),
        ("Sprint 3: Visualización MVP", today + timedelta(days=28), today + timedelta(days=42), "Planning", "Crear primeros dashboards")
    ]
    
    sprint_ids = {}
    for name, start, end, status, goal in sprints:
        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Dates": {"date": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")}},
            "Status": {"select": {"name": status}},
            "Goal": {"rich_text": [{"text": {"content": goal}}]}
        }
        sprint_ids[name] = create_page(sprints_db_id, props)
        print(f"    ✅ {name}")
    
    # Create Tasks
    tasks = [
        ("Configurar variables de entorno", "Feature", "High", "S (1-2h)", "Epic A: Ingesta de Datos", "Sprint 1: Setup & Ingesta Inicial"),
        ("Implementar ingesta FBRef", "Feature", "High", "M (3-5h)", "Epic A: Ingesta de Datos", "Sprint 1: Setup & Ingesta Inicial"),
        ("Implementar ingesta Sofascore", "Feature", "High", "M (3-5h)", "Epic A: Ingesta de Datos", "Sprint 1: Setup & Ingesta Inicial"),
        ("Configurar proyecto dbt", "Feature", "Medium", "M (3-5h)", "Epic B: Transformación de Datos", "Sprint 2: Transformaciones dbt"),
        ("Crear modelos staging", "Feature", "Medium", "L (1-2d)", "Epic B: Transformación de Datos", "Sprint 2: Transformaciones dbt"),
        ("Documentar arquitectura", "Documentation", "Low", "S (1-2h)", "Epic A: Ingesta de Datos", None),
        ("Investigar APIs tiempo real", "Research", "Low", "M (3-5h)", "Epic A: Ingesta de Datos", None)
    ]
    
    for name, type_, priority, effort, epic, sprint in tasks:
        props = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Type": {"select": {"name": type_}},
            "Priority": {"select": {"name": priority}},
            "Effort": {"select": {"name": effort}}
        }
        if epic and epic in epic_ids:
            props["Epic"] = {"relation": [{"id": epic_ids[epic]}]}
        if sprint and sprint in sprint_ids:
            props["Sprint"] = {"relation": [{"id": sprint_ids[sprint]}]}
        
        create_page(tasks_db_id, props)
        print(f"    ✅ {name}")
    
    print("  Initial data seeded successfully!")


def main():
    """Main entry point for the PM infrastructure setup."""
    print("=" * 60)
    print("🚀 SportsAnalytics - Notion PM Infrastructure Setup")
    print("=" * 60)
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    validate_config()
    print("  Configuration valid!")
    
    # Verify connection
    print("\n🔌 Connecting to Notion API...")
    response = httpx.get(
        f"https://api.notion.com/v1/pages/{NOTION_PAGE_ID}",
        headers=get_headers(),
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"\n❌ Failed to connect to Notion:")
        print(f"  {response.json().get('message', response.text)}")
        print("\n💡 Make sure you have:")
        print("  1. Connected your integration to the target page")
        print("  2. Used the correct page ID")
        sys.exit(1)
    
    print("  Connected successfully!")
    
    # Create databases
    print("\n🏗️ Creating PM databases...")
    
    epics_db_id = setup_epics_db(NOTION_PAGE_ID)
    sprints_db_id = setup_sprints_db(NOTION_PAGE_ID)
    tasks_db_id = setup_tasks_db(NOTION_PAGE_ID, epics_db_id, sprints_db_id)
    
    # Wait for Notion to sync
    print("\n⏳ Waiting for Notion to sync...")
    time.sleep(2)
    
    # Seed initial data
    seed_initial_data(epics_db_id, sprints_db_id, tasks_db_id)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ PM Infrastructure deployed successfully!")
    print("=" * 60)
    print("\n📊 Created databases:")
    print(f"  - DB Epics:  {epics_db_id}")
    print(f"  - DB Sprints: {sprints_db_id}")
    print(f"  - DB Tasks:   {tasks_db_id}")
    
    print("\n📝 Next steps:")
    print("  1. Go to Notion and refresh your page")
    print("  2. Create a 'Sprint Board' page with a linked view of Tasks DB")
    print("  3. Set the view layout to 'Board' and group by 'Status'")
    print("  4. Add a filter: 'Sprint' contains your current sprint")
    print("  5. Configure Notion MCP in Cursor (see README_MCP.md)")
    
    return {
        "epics_db_id": epics_db_id,
        "sprints_db_id": sprints_db_id,
        "tasks_db_id": tasks_db_id
    }


if __name__ == "__main__":
    main()
