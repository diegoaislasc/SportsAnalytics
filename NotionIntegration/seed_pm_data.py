#!/usr/bin/env python3
"""
Seed initial data into existing Notion PM databases.
Uses raw HTTP requests with explicit API version for compatibility.
"""

import os
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# Database IDs
EPICS_DB_ID = "c7be23a3-d0bf-45e0-85ea-dc8a35d3f6e5"
SPRINTS_DB_ID = "a3aab924-e346-43d7-beb5-471cce904680"
TASKS_DB_ID = "0c62367d-2bf8-4956-8b96-32e93382acec"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}


def create_page(database_id: str, properties: dict) -> str:
    """Create a page in a database."""
    response = httpx.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json={
            "parent": {"database_id": database_id},
            "properties": properties
        }
    )
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"    Error: {response.status_code} - {response.json().get('message', '')}")
        raise Exception(f"Failed to create page: {response.text}")


def main():
    print("🌱 Seeding SportsAnalytics PM databases...\n")
    
    # Create Epics
    print("📦 Creating Epics...")
    epics = [
        {
            "name": "Epic A: Ingesta de Datos",
            "description": "Configurar pipelines de extracción de datos desde APIs deportivas (FBRef, Sofascore)",
            "status": "In Progress",
            "priority": "High"
        },
        {
            "name": "Epic B: Transformación de Datos",
            "description": "Implementar modelos dbt para transformar datos crudos en métricas analíticas",
            "status": "Backlog",
            "priority": "High"
        },
        {
            "name": "Epic C: Visualización y Predicciones",
            "description": "Crear dashboards y modelos ML para análisis predictivo de rendimiento",
            "status": "Backlog",
            "priority": "Medium"
        }
    ]
    
    epic_ids = {}
    for epic in epics:
        props = {
            "Name": {"title": [{"text": {"content": epic["name"]}}]},
            "Description": {"rich_text": [{"text": {"content": epic["description"]}}]},
            "Status": {"select": {"name": epic["status"]}},
            "Priority": {"select": {"name": epic["priority"]}},
            "Progress": {"number": 0}
        }
        epic_id = create_page(EPICS_DB_ID, props)
        epic_ids[epic["name"]] = epic_id
        print(f"  ✅ {epic['name']}")
    
    # Create Sprints
    print("\n🏃 Creating Sprints...")
    today = datetime.now()
    sprints = [
        {
            "name": "Sprint 1: Setup & Ingesta Inicial",
            "start": today,
            "end": today + timedelta(days=14),
            "status": "Active",
            "goal": "Configurar infraestructura base y primeros scripts de ingesta"
        },
        {
            "name": "Sprint 2: Transformaciones dbt",
            "start": today + timedelta(days=14),
            "end": today + timedelta(days=28),
            "status": "Planning",
            "goal": "Implementar modelos de staging y marts en dbt"
        },
        {
            "name": "Sprint 3: Visualización MVP",
            "start": today + timedelta(days=28),
            "end": today + timedelta(days=42),
            "status": "Planning",
            "goal": "Crear primeros dashboards con métricas clave"
        }
    ]
    
    sprint_ids = {}
    for sprint in sprints:
        props = {
            "Name": {"title": [{"text": {"content": sprint["name"]}}]},
            "Dates": {
                "date": {
                    "start": sprint["start"].strftime("%Y-%m-%d"),
                    "end": sprint["end"].strftime("%Y-%m-%d")
                }
            },
            "Status": {"select": {"name": sprint["status"]}},
            "Goal": {"rich_text": [{"text": {"content": sprint["goal"]}}]}
        }
        sprint_id = create_page(SPRINTS_DB_ID, props)
        sprint_ids[sprint["name"]] = sprint_id
        print(f"  ✅ {sprint['name']}")
    
    # Create Tasks
    print("\n✅ Creating Tasks...")
    tasks = [
        {
            "name": "Configurar variables de entorno para APIs",
            "type": "Feature",
            "priority": "High",
            "effort": "S (1-2h)",
            "epic": "Epic A: Ingesta de Datos",
            "sprint": "Sprint 1: Setup & Ingesta Inicial"
        },
        {
            "name": "Implementar script de ingesta para FBRef",
            "type": "Feature",
            "priority": "High",
            "effort": "M (3-5h)",
            "epic": "Epic A: Ingesta de Datos",
            "sprint": "Sprint 1: Setup & Ingesta Inicial"
        },
        {
            "name": "Implementar script de ingesta para Sofascore",
            "type": "Feature",
            "priority": "High",
            "effort": "M (3-5h)",
            "epic": "Epic A: Ingesta de Datos",
            "sprint": "Sprint 1: Setup & Ingesta Inicial"
        },
        {
            "name": "Configurar proyecto dbt con BigQuery",
            "type": "Feature",
            "priority": "Medium",
            "effort": "M (3-5h)",
            "epic": "Epic B: Transformación de Datos",
            "sprint": "Sprint 2: Transformaciones dbt"
        },
        {
            "name": "Crear modelos de staging para datos crudos",
            "type": "Feature",
            "priority": "Medium",
            "effort": "L (1-2d)",
            "epic": "Epic B: Transformación de Datos",
            "sprint": "Sprint 2: Transformaciones dbt"
        },
        {
            "name": "Documentar arquitectura de datos",
            "type": "Documentation",
            "priority": "Low",
            "effort": "S (1-2h)",
            "epic": "Epic A: Ingesta de Datos",
            "sprint": None
        },
        {
            "name": "Investigar APIs de datos en tiempo real",
            "type": "Research",
            "priority": "Low",
            "effort": "M (3-5h)",
            "epic": "Epic A: Ingesta de Datos",
            "sprint": None
        }
    ]
    
    for task in tasks:
        props = {
            "Name": {"title": [{"text": {"content": task["name"]}}]},
            "Type": {"select": {"name": task["type"]}},
            "Priority": {"select": {"name": task["priority"]}},
            "Effort": {"select": {"name": task["effort"]}}
        }
        
        if task["epic"] and task["epic"] in epic_ids:
            props["Epic"] = {"relation": [{"id": epic_ids[task["epic"]]}]}
        
        if task["sprint"] and task["sprint"] in sprint_ids:
            props["Sprint"] = {"relation": [{"id": sprint_ids[task["sprint"]]}]}
        
        create_page(TASKS_DB_ID, props)
        print(f"  ✅ {task['name']}")
    
    print("\n" + "=" * 60)
    print("✅ PM data seeded successfully!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Go to Notion and refresh your page:")
    print("     https://www.notion.so/Data-Sports-fe31c9bc8c164714bf0c06140eb12c26")
    print("  2. Create a 'Sprint Board' linked view of DB Tasks")
    print("  3. Set view layout to 'Board' and group by 'Status'")
    print("  4. Configure Notion MCP in Cursor (see README_MCP.md)")


if __name__ == "__main__":
    main()
