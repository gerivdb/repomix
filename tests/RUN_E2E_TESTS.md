# ENV2 E2E Tests — Guide d'Exécution

## Comment tester que le middleware fonctionne réellement

### Prérequis

1. **Avoir un navigateur Chromium** (Chrome, Edge, Brave, ou Comet)
2. **Avoir Python 3.8+** avec les dépendances installées

### Étape 1: Lancer le navigateur avec CDP

#### Option A: Chrome (recommandé)
```bash
# Fermez d'abord tous les Chrome existants, puis:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

#### Option B: Edge
```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
```

#### Option C: Brave
```bash
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
```

### Étape 2: Exécuter les tests E2E

#### Mode interactif (recommandé)
```bash
cd d:\DO\WEB\TOOLS\L0-CANON\NEXUS
python tests/test_env2_e2e_comet.py
```

Le script vous proposera 3 options:
1. **Tests unitaires** — Exécute les tests automatisés
2. **Test manuel interactif** — Test guidé pas à pas
3. **Tous les tests** — Exécute tout

#### Mode automatique
```bash
python -m pytest tests/test_env2_e2e_comet.py -v
```

### Étape 3: Interpréter les résultats

#### ✅ Succès
```
✅ CDP disponible: Chrome/120.0.xxx.xxx
📋 Tabs trouvées: 5
  1. Google - https://www.google.com
  2. GitHub - https://github.com
...
✅ Tests manuels complétés avec succès!
```

#### ⚠️ Échec — Navigateur non lancé
```
⚠️ CDP non disponible - Lancez Chrome avec --remote-debugging-port=9222
```
→ Solution: Lancez Chrome comme indiqué à l'étape 1.

#### ❌ Échec — Port déjà utilisé
```
ERROR: Port 9222 already in use
```
→ Solution: Fermez les autres instances Chrome ou utilisez un autre port (`--port 9223`).

### Test rapide en une ligne

```bash
# Lance Chrome + exécute un test basique
python -c "
from managers.cdp_client import CDPClient
client = CDPClient()
if client.is_available():
    tabs = client.list_targets()
    print(f'✅ {len(tabs)} tabs trouvées')
else:
    print('❌ Aucun navigateur CDP disponible')
"
```

### Vérifier chaque composant individuellement

```bash
# 1. Vérifier CDP
python -c "from managers.comet_launcher import check_cdp_available; print(check_cdp_available('localhost', 9222))"

# 2. Lister les tabs
python -c "from managers.cdp_client import CDPClient; c = CDPClient(); print([t.title for t in c.list_targets()])"

# 3. Classifier une tab
python -c "from managers.env2_tab_harvest import classify_tab; print(classify_tab('https://github.com/gerivdb/NEXUS', 'NEXUS'))"

# 4. Vérifier santé
python -c "from managers.auto_heal import BrowserHealthChecker; print(BrowserHealthChecker().check())"
```

### Dashboard Web (Phase 13)

Pour tester le dashboard:

```bash
# Installer les dépendances
pip install fastapi uvicorn websockets jinja2

# Lancer le dashboard
python managers/dashboard/app.py --port 8080

# Ouvrir dans le navigateur
# http://localhost:8080
```

### WebSocket Server (Phase 12)

Pour tester le serveur d'événements:

```bash
# Lancer le server
python managers/event_server.py --port 8765

# Dans un autre terminal, tester la connexion
python -c "
import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send('{\"action\": \"subscribe\", \"filters\": [\"all\"]}')
        response = await ws.recv()
        print(f'✅ Response: {response}')

asyncio.run(test())
```

### Dépannage

| Problème | Solution |
|----------|----------|
| "CDP non disponible" | Lancez Chrome avec `--remote-debugging-port=9222` |
| "Port already in use" | Tuez les processus Chrome: `taskkill /F /IM chrome.exe` |
| "Module not found" | `pip install -r tools/requirements.txt` |
| "Access denied" | Exécutez en tant qu'administrateur |

### Validation complète

Pour une validation complète du middleware:

```bash
# 1. Tests unitaires (mocks)
python -m pytest tests/test_env2_full.py -v

# 2. Tests industrialization
python -m pytest tests/test_env2_industrialization.py -v

# 3. Tests E2E (nécessite Chrome lancé)
python -m pytest tests/test_env2_e2e_comet.py -v

# Total attendu: 46+ tests pass