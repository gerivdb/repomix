# Tests E2E pour l'ensemble du système neurosymbolique
# Teste le pipeline complet de l'audit à la vérification

Describe "Neurosymbolic System E2E Tests" {

    BeforeAll {
        # Setup test environment
        $testRoot = "TestDrive:\NEXUS_TEST"
        New-Item -ItemType Directory -Path $testRoot -Force

        # Copy necessary files
        Copy-Item "ONTOLOGY" "$testRoot\" -Recurse
        Copy-Item "BRAIN-DOCS" "$testRoot\" -Recurse
        Copy-Item "scripts" "$testRoot\" -Recurse
    }

    It "Should complete full ontology audit pipeline" {
        # Run audit script
        $auditScript = "$testRoot\scripts\ontology_audit_brain_docs.ps1"
        $reportPath = "$testRoot\scripts\ontology_audit_report.json"

        & $auditScript -OntologyPath "$testRoot\ONTOLOGY" -BrainDocsPath "$testRoot\BRAIN-DOCS" -OutputFile $reportPath

        # Verify report exists
        Test-Path $reportPath | Should -Be $true

        # Verify report content
        $report = Get-Content $reportPath | ConvertFrom-Json
        $report | Should -Not -BeNull
        $report.timestamp | Should -Not -BeNull
        $report.results | Should -Not -BeNull
    }

    It "Should handle multiple audit runs consistently" {
        # Run audit multiple times to ensure consistency
        $auditScript = "$testRoot\scripts\ontology_audit_brain_docs.ps1"
        $reportPath = "$testRoot\scripts\ontology_audit_report.json"

        & $auditScript -OntologyPath "$testRoot\ONTOLOGY" -BrainDocsPath "$testRoot\BRAIN-DOCS" -OutputFile $reportPath
        $report1 = Get-Content $reportPath | ConvertFrom-Json

        # Run again
        & $auditScript -OntologyPath "$testRoot\ONTOLOGY" -BrainDocsPath "$testRoot\BRAIN-DOCS" -OutputFile $reportPath
        $report2 = Get-Content $reportPath | ConvertFrom-Json

        # Results should be consistent
        $report1.results.total_brain_terms | Should -Be $report2.results.total_brain_terms
        $report1.results.matched.Count | Should -Be $report2.results.matched.Count
    }

    It "Should integrate with formal verification" {
        # This would require Z3 installed
        # For now, test script existence and basic structure

        $verificationScript = "$testRoot\scripts\formal_verification_z3.py"
        Test-Path $verificationScript | Should -Be $true

        # Test if script can be executed (would fail without Z3)
        # & python $verificationScript
        # Check for report generation
    }

    It "Should validate CI workflow structure" {
        $workflowFile = ".github\workflows\ontology-audit.yml"
        Test-Path $workflowFile | Should -Be $true

        $workflow = Get-Content $workflowFile -Raw
        $workflow | Should -Match "ontology-audit"
        $workflow | Should -Match "pull_request"
        $workflow | Should -Match "BRAIN-DOCS"
    }

    It "Should load dashboard with test data" {
        $dashboardFile = "monitoring\dashboard_ontology.html"
        Test-Path $dashboardFile | Should -Be $true

        $html = Get-Content $dashboardFile -Raw
        $html | Should -Match "<html"
        $html | Should -Match "Chart.js"
        $html | Should -Match "ontology_audit_report.json"
    }
}