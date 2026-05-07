# Tests TDD pour Ontology Audit Script
# Utilise Pester pour tests unitaires

Describe "Ontology Audit Tests" {

    BeforeAll {
        # Setup test data
        $testOntologyPath = "TestDrive:\ONTOLOGY"
        $testBrainDocsPath = "TestDrive:\BRAIN-DOCS"
        $testOutputFile = "TestDrive:\audit_report.json"

        New-Item -ItemType Directory -Path $testOntologyPath -Force
        New-Item -ItemType Directory -Path $testBrainDocsPath -Force

        # Create test ontology file
        $testOntology = @{
            "TestTerm" = @{
                id = "test"
                name = "Test"
                domain = "test"
                definition = "N: Test term. N+1: Test definition. N+2: Test context."
            }
        } | ConvertTo-Json
        $testOntology | Out-File "$testOntologyPath\ontology_complete.json"

        # Create test brain-docs file
        "This contains TestTerm and UnknownTerm." | Out-File "$testBrainDocsPath\test.md"
    }

    It "Should load ontology terms correctly" {
        # Mock the function or test the logic
        # Since functions are internal, test the output

        # Run the script
        $scriptPath = "$PSScriptRoot\..\scripts\ontology_audit_brain_docs.ps1"
        & $scriptPath -OntologyPath $testOntologyPath -BrainDocsPath $testBrainDocsPath -OutputFile $testOutputFile

        $report = Get-Content $testOutputFile | ConvertFrom-Json

        $report.results.total_ontology_terms | Should -BeGreaterThan 0
        $report.results.matched | Should -Not -BeNull
        $report.results.missing | Should -Not -BeNull
    }

    It "Should detect matched and missing terms" {
        $scriptPath = "$PSScriptRoot\..\scripts\ontology_audit_brain_docs.ps1"
        & $scriptPath -OntologyPath $testOntologyPath -BrainDocsPath $testBrainDocsPath -OutputFile $testOutputFile

        $report = Get-Content $testOutputFile | ConvertFrom-Json

        # Should find TestTerm as matched
        $matchedTerms = $report.results.matched | Where-Object { $_.term -eq "TestTerm" }
        $matchedTerms | Should -Not -BeNull

        # Should find UnknownTerm as missing
        $missingTerms = $report.results.missing | Where-Object { $_.term -eq "UnknownTerm" }
        $missingTerms | Should -Not -BeNull
    }

    It "Should generate valid JSON report" {
        $scriptPath = "$PSScriptRoot\..\scripts\ontology_audit_brain_docs.ps1"
        & $scriptPath -OntologyPath $testOntologyPath -BrainDocsPath $testBrainDocsPath -OutputFile $testOutputFile

        $report = Get-Content $testOutputFile | ConvertFrom-Json

        $report.timestamp | Should -Not -BeNull
        $report.results | Should -Not -BeNull
        $report.results.total_brain_terms | Should -BeGreaterOrEqual 0
    }

    It "Should handle missing ontology file gracefully" {
        $invalidPath = "TestDrive:\INVALID"
        $scriptPath = "$PSScriptRoot\..\scripts\ontology_audit_brain_docs.ps1"

        { & $scriptPath -OntologyPath $invalidPath -BrainDocsPath $testBrainDocsPath -OutputFile $testOutputFile } | Should -Throw
    }
}