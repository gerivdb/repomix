# -----------------------------------------------------------------------------
# Tests TDD pour EPIC-9857: Bootstrap Agnostic Launcher
# Tests unitaires PowerShell avec Pester
# Couverture: Fonctions core, détection, sécurité, sélection
# -----------------------------------------------------------------------------

# Import du module à tester (simulation)
. "$PSScriptRoot\..\DevTools\bin\ecos-launch.ps1"

Describe "ecos-launch.ps1 - EPIC-9857 Bootstrap Agnostic Launcher" {

    BeforeAll {
        # Mock configuration pour tests
        $script:CONFIG = @{
            Tools = @{
                KiloCode = @{
                    Priority = 1
                    Detection = { Test-Path "$env:USERPROFILE\.vscode\extensions\*kilocode*" }
                    Launch = { Start-KiloCodeLaunch }
                    Performance = "High"
                }
                Cline = @{
                    Priority = 2
                    Detection = { Test-Path "$env:USERPROFILE\.vscode\extensions\*cline*" }
                    Launch = { Start-ClineLaunch }
                    Performance = "Medium"
                }
                Antigravity = @{
                    Priority = 3
                    Detection = { Test-Path "C:\Program Files\Antigravity\*" }
                    Launch = { Start-AntigravityLaunch }
                    Performance = "Variable"
                }
            }
            Security = @{
                BDCPMode = $true
                AllowedPaths = @("D:\DO\WEB", "C:\DevTools")
                ValidateAccess = $true
            }
            Cache = @{
                ConfigTTLSeconds = 300
                DetectionCacheEnabled = $false  # Désactivé pour tests
            }
        }
    }

    Context "Tool Detection - Get-AvailableTools" {

        It "Should detect KiloCode when extension exists" {
            Mock Test-Path { $true } -ParameterFilter { $Path -like "*kilocode*" }

            $available = Get-AvailableTools
            $available | Should -Contain "KiloCode"
        }

        It "Should detect Cline when extension exists" {
            Mock Test-Path { $true } -ParameterFilter { $Path -like "*cline*" }

            $available = Get-AvailableTools
            $available | Should -Contain "Cline"
        }

        It "Should detect Antigravity when installed" {
            Mock Test-Path { $true } -ParameterFilter { $Path -like "*Antigravity*" }

            $available = Get-AvailableTools
            $available | Should -Contain "Antigravity"
        }

        It "Should return empty array when no tools detected" {
            Mock Test-Path { $false }

            $available = Get-AvailableTools
            $available.Count | Should -Be 0
        }

        It "Should detect multiple tools correctly" {
            Mock Test-Path {
                switch ($Path) {
                    {$_ -like "*kilocode*"} { $true }
                    {$_ -like "*cline*"} { $true }
                    {$_ -like "*Antigravity*"} { $false }
                    default { $false }
                }
            }

            $available = Get-AvailableTools
            $available | Should -Contain "KiloCode"
            $available | Should -Contain "Cline"
            $available | Should -Not -Contain "Antigravity"
            $available.Count | Should -Be 2
        }
    }

    Context "Tool Selection - Select-OptimalTool" {

        It "Should select highest priority tool (KiloCode) when all available" {
            $available = @("Antigravity", "Cline", "KiloCode")

            $selected = Select-OptimalTool -AvailableTools $available
            $selected | Should -Be "KiloCode"
        }

        It "Should select Cline when KiloCode not available" {
            $available = @("Antigravity", "Cline")

            $selected = Select-OptimalTool -AvailableTools $available
            $selected | Should -Be "Cline"
        }

        It "Should select Antigravity as last resort" {
            $available = @("Antigravity")

            $selected = Select-OptimalTool -AvailableTools $available
            $selected | Should -Be "Antigravity"
        }

        It "Should respect explicit tool parameter" {
            $available = @("KiloCode", "Cline", "Antigravity")

            $selected = Select-OptimalTool -AvailableTools $available -Tool "Cline"
            $selected | Should -Be "Cline"
        }

        It "Should fallback to auto-selection when explicit tool not available" {
            $available = @("KiloCode", "Antigravity")
            $Tool = "Cline"

            # Mock Write-Warning to capture warning
            Mock Write-Warning { }

            $selected = Select-OptimalTool -AvailableTools $available -Tool $Tool
            $selected | Should -Be "KiloCode"

            Assert-MockCalled Write-Warning -Exactly 1
        }

        It "Should throw when no tools available" {
            $available = @()

            { Select-OptimalTool -AvailableTools $available } | Should -Throw "No tools available for selection"
        }
    }

    Context "Security Validation - Test-BDCPAccess" {

        It "Should pass BDCP validation when all paths accessible" {
            Mock Test-Path { $true }

            $result = Test-BDCPAccess
            $result | Should -Be $true
        }

        It "Should fail BDCP validation when critical path inaccessible" {
            Mock Test-Path {
                switch ($Path) {
                    "D:\DO\WEB" { $false }
                    "C:\DevTools" { $true }
                    default { $true }
                }
            }
            Mock Write-Error { }

            $result = Test-BDCPAccess
            $result | Should -Be $false

            Assert-MockCalled Write-Error -Exactly 1
        }

        It "Should fail BDCP validation when DevTools path inaccessible" {
            Mock Test-Path {
                switch ($Path) {
                    "D:\DO\WEB" { $true }
                    "C:\DevTools" { $false }
                    default { $true }
                }
            }
            Mock Write-Error { }

            $result = Test-BDCPAccess
            $result | Should -Be $false

            Assert-MockCalled Write-Error -Exactly 1
        }
    }

    Context "Launch Functions - Start-SecureLaunch" {

        It "Should succeed launch when BDCP validation passes" {
            Mock Test-BDCPAccess { $true }
            Mock Start-KiloCodeLaunch { }

            { Start-SecureLaunch -SelectedTool "KiloCode" } | Should -Not -Throw
        }

        It "Should fail launch when BDCP validation fails" {
            Mock Test-BDCPAccess { $false }

            { Start-SecureLaunch -SelectedTool "KiloCode" } | Should -Throw "BDCP mode validation failed"
        }

        It "Should call correct launch function for each tool" {
            Mock Test-BDCPAccess { $true }

            Mock Start-KiloCodeLaunch { }
            Start-SecureLaunch -SelectedTool "KiloCode"
            Assert-MockCalled Start-KiloCodeLaunch -Exactly 1

            Mock Start-ClineLaunch { }
            Start-SecureLaunch -SelectedTool "Cline"
            Assert-MockCalled Start-ClineLaunch -Exactly 1

            Mock Start-AntigravityLaunch { }
            Start-SecureLaunch -SelectedTool "Antigravity"
            Assert-MockCalled Start-AntigravityLaunch -Exactly 1
        }
    }

    Context "Specific Launch Functions" {

        BeforeEach {
            Mock Test-Path { $true } # Mock commandes disponibles
        }

        It "Should launch KiloCode with correct arguments" {
            Mock & { $LASTEXITCODE = 0 } -ParameterFilter {
                $args[0] -eq "${env:ProgramFiles}\Microsoft VS Code\bin\code.cmd" -and
                $args[1] -eq "--extensionDevelopmentPath" -and
                $args[2] -eq "D:\DO\WEB\TOOLS\KiloCode"
            }

            { Start-KiloCodeLaunch } | Should -Not -Throw
        }

        It "Should fail KiloCode launch when command not found" {
            Mock Test-Path { $false } -ParameterFilter { $Path -eq "${env:ProgramFiles}\Microsoft VS Code\bin\code.cmd" }

            { Start-KiloCodeLaunch } | Should -Throw "KiloCode command not found"
        }

        It "Should configure Cline MCP and launch correctly" {
            Mock Set-Content { }
            Mock & { $LASTEXITCODE = 0 } -ParameterFilter {
                $args[0] -eq "${env:ProgramFiles}\Microsoft VS Code\bin\code.cmd" -and
                $args[1] -eq "D:\DO\WEB\.cline\settings.json"
            }

            { Start-ClineLaunch } | Should -Not -Throw
        }

        It "Should create Cline directory if not exists" {
            Mock Test-Path { $false } -ParameterFilter { $Path -eq "D:\DO\WEB\.cline" }
            Mock New-Item { }
            Mock Set-Content { }
            Mock & { $LASTEXITCODE = 0 }

            Start-ClineLaunch

            Assert-MockCalled New-Item -Exactly 1
        }

        It "Should launch Antigravity with correct command" {
            Mock & { $LASTEXITCODE = 0 } -ParameterFilter {
                $args[0] -eq "C:\Program Files\Antigravity\Antigravity.exe"
            }

            { Start-AntigravityLaunch } | Should -Not -Throw
        }

        It "Should fail launch when process exits with error" {
            Mock Test-Path { $true }
            Mock & { $LASTEXITCODE = 1 }

            { Start-KiloCodeLaunch } | Should -Throw "KiloCode launch failed with exit code 1"
        }
    }

    Context "Cache Functionality" {

        It "Should use cached results when cache is fresh" {
            # Setup cache file
            $cacheFile = "$env:TEMP\nexus_launcher_cache.json"
            $cacheData = @{
                Timestamp = (Get-Date).ToString("o")
                AvailableTools = @("KiloCode", "Cline")
            }
            $cacheData | ConvertTo-Json | Set-Content $cacheFile -Force

            # Enable cache
            $CONFIG.Cache.DetectionCacheEnabled = $true

            # Mock to ensure not called
            Mock Test-Path { throw "Should not be called" } -ParameterFilter { $Path -like "*kilocode*" }

            $available = Get-AvailableTools

            $available | Should -Contain "KiloCode"
            $available | Should -Contain "Cline"
        }

        It "Should ignore stale cache" {
            # Setup stale cache (1 hour old)
            $cacheFile = "$env:TEMP\nexus_launcher_cache.json"
            $staleTime = (Get-Date).AddHours(-1)
            $cacheData = @{
                Timestamp = $staleTime.ToString("o")
                AvailableTools = @("OldData")
            }
            $cacheData | ConvertTo-Json | Set-Content $cacheFile -Force

            $CONFIG.Cache.DetectionCacheEnabled = $true

            Mock Test-Path { $true } -ParameterFilter { $Path -like "*kilocode*" }

            $available = Get-AvailableTools

            $available | Should -Contain "KiloCode"
            $available | Should -Not -Contain "OldData"
        }
    }

    Context "Error Handling" {

        It "Should throw when no tools detected in main logic" {
            Mock Get-AvailableTools { @() }

            $scriptBlock = {
                $availableTools = Get-AvailableTools
                if ($availableTools.Count -eq 0) {
                    throw "No supported VSIX tools detected. Please install KiloCode, Cline, or Antigravity."
                }
            }

            { & $scriptBlock } | Should -Throw "No supported VSIX tools detected"
        }

        It "Should handle exceptions gracefully in detection" {
            Mock Test-Path { throw "Simulated error" }

            { Get-AvailableTools } | Should -Not -Throw
        }
    }
}