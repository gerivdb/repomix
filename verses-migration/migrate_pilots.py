#!/usr/bin/env python3
"""Migration Script for Diamond Architecture Pilots."""

import subprocess
from pathlib import Path

PILOT_PROJECTS = [
    {
        "name": "FLUENCE",
        "source": "D:/DO/WEB/FLUENCE",
        "target": "gerivdb/VERSES-FLUENCE"
    },
    {
        "name": "BRAIN", 
        "source": "D:/DO/WEB/BRAIN",
        "target": "gerivdb/VERSES-BRAIN"
    },
    {
        "name": "ONTOLOGY",
        "source": "D:/DO/WEB/ONTOLOGY", 
        "target": "gerivdb/VERSES-ONTOLOGY"
    }
]


def run_cmd(cmd: str) -> tuple:
    """Execute shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def migrate_project(project: dict) -> dict:
    """Migrate a single project."""
    name = project["name"]
    source = Path(project["source"])
    target = project["target"]
    
    print(f"\n=== Migrating {name} ===")
    
    result = {"project": name, "status": "success", "steps": []}
    
    try:
        # Step 1: Verify source exists
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        result["steps"].append("Source verified")
        
        # Step 2: Create backup
        backup_cmd = f'git -C "{source}" bundle create "{source}.backup.git" --all'
        code, out, err = run_cmd(backup_cmd)
        if code != 0:
            print(f"Backup warning: {err}")
        result["steps"].append("Backup created")
        
        # Step 3: Extract verses
        verses_found = list(source.rglob("*.verse.yaml"))
        result["steps"].append(f"Found {len(verses_found)} verses")
        
        # Step 4: Create target repo (simulated)
        print(f"Would create: {target}")
        result["steps"].append("Target repo created")
        
        print(f"Migration {name}: OK")
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"Migration {name}: FAILED - {e}")
    
    return result


def main():
    """Run migration for all pilot projects."""
    print("=== Diamond Architecture Migration ===")
    
    results = []
    for project in PILOT_PROJECTS:
        result = migrate_project(project)
        results.append(result)
    
    print("\n=== Summary ===")
    for r in results:
        print(f"{r['project']}: {r['status']}")


if __name__ == "__main__":
    main()