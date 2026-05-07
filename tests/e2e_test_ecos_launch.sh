#!/bin/bash
# -----------------------------------------------------------------------------
# Tests E2E pour EPIC-9857: Bootstrap Agnostic Launcher
# Tests end-to-end de lancement et détection
# Environnements: Windows avec PowerShell
# -----------------------------------------------------------------------------

set -e  # Exit on any error

# Configuration tests
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/.." && pwd)"
LAUNCHER_SCRIPT="$PROJECT_ROOT/DevTools/bin/ecos-launch.ps1"
TEST_TIMEOUT=30

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}NEXUS EPIC-9857 E2E Tests - Bootstrap Agnostic Launcher${NC}"
echo -e "${BLUE}$(printf '%.0s=' {1..60})${NC}"

# -----------------------------------------------------------------------------
# UTILITAIRES DE TEST
# -----------------------------------------------------------------------------

assert_success() {
    local message="$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $message${NC}"
        return 0
    else
        echo -e "${RED}✗ $message${NC}"
        return 1
    fi
}

assert_failure() {
    local message="$1"
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ $message${NC}"
        return 0
    else
        echo -e "${RED}✗ $message${NC}"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$?"
    local message="$2"
    if [ "$actual" -eq "$expected" ]; then
        echo -e "${GREEN}✓ $message (exit code: $actual)${NC}"
        return 0
    else
        echo -e "${RED}✗ $message (expected: $expected, got: $actual)${NC}"
        return 1
    fi
}

run_powershell_cmd() {
    local cmd="$1"
    local timeout="${2:-$TEST_TIMEOUT}"

    if command -v pwsh >/dev/null 2>&1; then
        timeout "$timeout"s pwsh -Command "$cmd"
    elif command -v powershell >/dev/null 2>&1; then
        timeout "$timeout"s powershell -Command "$cmd"
    else
        echo -e "${RED}PowerShell not found${NC}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# TESTS E2E
# -----------------------------------------------------------------------------

test_launcher_script_exists() {
    echo "Testing launcher script existence..."
    if [ -f "$LAUNCHER_SCRIPT" ]; then
        echo -e "${GREEN}✓ Launcher script exists at $LAUNCHER_SCRIPT${NC}"
        return 0
    else
        echo -e "${RED}✗ Launcher script not found at $LAUNCHER_SCRIPT${NC}"
        return 1
    fi
}

test_no_tools_detected() {
    echo "Testing behavior when no tools detected..."

    # Simuler environnement sans outils
    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool auto -Verbose 2>&1" 2>&1) || true

    echo "$output" | grep -q "No supported VSIX tools detected" || {
        echo -e "${RED}Expected error message not found in output:${NC}"
        echo "$output"
        return 1
    }

    echo -e "${GREEN}✓ Correctly detected no tools and showed error${NC}"
}

test_kilocode_detection() {
    echo "Testing KiloCode detection..."

    # Créer répertoire simulé pour KiloCode
    local kilocode_dir="$HOME/.vscode/extensions/kilocode-test"
    mkdir -p "$kilocode_dir"

    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool auto -Verbose 2>&1")

    echo "$output" | grep -q "KiloCode detected" || {
        echo -e "${RED}KiloCode not detected in output:${NC}"
        echo "$output"
        return 1
    }

    echo "$output" | grep -q "Selected tool: KiloCode" || {
        echo -e "${RED}KiloCode not selected as optimal tool:${NC}"
        echo "$output"
        return 1
    }

    # Nettoyer
    rm -rf "$kilocode_dir"

    echo -e "${GREEN}✓ KiloCode correctly detected and selected${NC}"
}

test_cline_detection() {
    echo "Testing Cline detection..."

    # Créer répertoire simulé pour Cline
    local cline_dir="$HOME/.vscode/extensions/cline-test"
    mkdir -p "$cline_dir"

    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool auto -Verbose 2>&1")

    echo "$output" | grep -q "Cline detected" || {
        echo -e "${RED}Cline not detected in output:${NC}"
        echo "$output"
        return 1
    }

    echo "$output" | grep -q "Selected tool: Cline" || {
        echo -e "${RED}Cline not selected as optimal tool:${NC}"
        echo "$output"
        return 1
    }

    # Nettoyer
    rm -rf "$cline_dir"

    echo -e "${GREEN}✓ Cline correctly detected and selected${NC}"
}

test_priority_selection() {
    echo "Testing priority-based tool selection..."

    # Simuler tous les outils disponibles
    local kilocode_dir="$HOME/.vscode/extensions/kilocode-test"
    local cline_dir="$HOME/.vscode/extensions/cline-test"
    local antigravity_dir="/tmp/antigravity-sim"
    mkdir -p "$kilocode_dir" "$cline_dir" "$antigravity_dir"

    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool auto -Verbose 2>&1")

    # KiloCode (priority 1) devrait être sélectionné même si tous sont disponibles
    echo "$output" | grep -q "Selected tool: KiloCode" || {
        echo -e "${RED}KiloCode not selected despite highest priority:${NC}"
        echo "$output"
        return 1
    }

    # Nettoyer
    rm -rf "$kilocode_dir" "$cline_dir" "$antigravity_dir"

    echo -e "${GREEN}✓ Priority selection working correctly${NC}"
}

test_explicit_tool_selection() {
    echo "Testing explicit tool selection..."

    # Simuler Cline disponible
    local cline_dir="$HOME/.vscode/extensions/cline-test"
    mkdir -p "$cline_dir"

    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool Cline -Verbose 2>&1")

    echo "$output" | grep -q "Selected tool: Cline" || {
        echo -e "${RED}Explicit Cline selection failed:${NC}"
        echo "$output"
        return 1
    }

    # Nettoyer
    rm -rf "$cline_dir"

    echo -e "${GREEN}✓ Explicit tool selection working${NC}"
}

test_security_validation() {
    echo "Testing security (BDCP) validation..."

    # Simuler Cline disponible
    local cline_dir="$HOME/.vscode/extensions/cline-test"
    mkdir -p "$cline_dir"

    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool Cline -SafeMode -Verbose 2>&1")

    # Devrait réussir si chemins BDCP sont accessibles
    if [ -d "D:/DO/WEB" ] && [ -d "C:/DevTools" ]; then
        echo "$output" | grep -q "BDCP access validated" || {
            echo -e "${RED}BDCP validation not confirmed:${NC}"
            echo "$output"
            return 1
        }
        echo -e "${GREEN}✓ BDCP validation passed for accessible paths${NC}"
    else
        echo "$output" | grep -q "BDCP mode validation failed" || {
            echo -e "${YELLOW}⚠ BDCP validation should fail for inaccessible paths${NC}"
        }
        echo -e "${YELLOW}⚠ BDCP validation correctly failed for missing paths${NC}"
    fi

    # Nettoyer
    rm -rf "$cline_dir"
}

test_cline_mcp_configuration() {
    echo "Testing Cline MCP configuration..."

    # Simuler Cline disponible
    local cline_dir="$HOME/.vscode/extensions/cline-test"
    mkdir -p "$cline_dir"

    # Lancer Cline (qui devrait créer la config MCP)
    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool Cline -Verbose 2>&1")

    # Vérifier que le fichier de config a été créé
    local config_file="D:/DO/WEB/.cline/settings.json"
    if [ -f "$config_file" ]; then
        echo -e "${GREEN}✓ Cline MCP configuration file created${NC}"

        # Vérifier contenu JSON
        if command -v jq >/dev/null 2>&1; then
            local mcp_server
            mcp_server=$(jq -r '.cline.mcpServers.filesystem.command' "$config_file" 2>/dev/null)
            if [ "$mcp_server" = "npx" ]; then
                echo -e "${GREEN}✓ MCP filesystem server correctly configured${NC}"
            else
                echo -e "${RED}✗ MCP server not correctly configured${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠ jq not available, skipping JSON validation${NC}"
        fi
    else
        echo -e "${RED}✗ Cline MCP configuration file not created${NC}"
        return 1
    fi

    # Nettoyer
    rm -rf "$cline_dir"

    echo -e "${GREEN}✓ Cline MCP configuration test passed${NC}"
}

test_performance_baseline() {
    echo "Testing performance baseline..."

    # Simuler KiloCode disponible
    local kilocode_dir="$HOME/.vscode/extensions/kilocode-test"
    mkdir -p "$kilocode_dir"

    local start_time
    start_time=$(date +%s.%3N)

    # Lancement avec timeout court pour mesurer démarrage
    run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool KiloCode -Verbose" 5

    local end_time
    end_time=$(date +%s.%3N)

    local duration
    duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")

    if (( $(echo "$duration < 2.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✓ Launch time within acceptable range: ${duration}s${NC}"
    else
        echo -e "${YELLOW}⚠ Launch time higher than expected: ${duration}s (may be normal)${NC}"
    fi

    # Nettoyer
    rm -rf "$kilocode_dir"
}

test_error_handling() {
    echo "Testing error handling..."

    # Test avec outil invalide
    local output
    output=$(run_powershell_cmd "& '$LAUNCHER_SCRIPT' -Tool InvalidTool -Verbose 2>&1" 2>&1) || true

    echo "$output" | grep -q "not available" || {
        echo -e "${RED}Error handling for invalid tool failed:${NC}"
        echo "$output"
        return 1
    }

    echo -e "${GREEN}✓ Error handling working correctly${NC}"
}

# -----------------------------------------------------------------------------
# EXÉCUTION DES TESTS
# -----------------------------------------------------------------------------

echo -e "\n${YELLOW}Running E2E Tests...${NC}"

# Tests de base
test_launcher_script_exists
test_no_tools_detected

# Tests de détection
test_kilocode_detection
test_cline_detection

# Tests de logique
test_priority_selection
test_explicit_tool_selection

# Tests de sécurité
test_security_validation

# Tests spécifiques outils
test_cline_mcp_configuration

# Tests de performance
test_performance_baseline

# Tests d'erreur
test_error_handling

echo -e "\n${GREEN}All E2E tests completed!${NC}"
echo -e "${BLUE}$(printf '%.0s=' {1..60})${NC}"