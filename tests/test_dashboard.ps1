# Tests pour le dashboard de monitoring ontologique

Describe "Ontology Dashboard Tests" {

    It "Should have valid HTML structure" {
        $dashboardPath = "monitoring\dashboard_ontology.html"
        Test-Path $dashboardPath | Should -Be $true

        $html = Get-Content $dashboardPath -Raw
        $html | Should -Match "<!DOCTYPE html>"
        $html | Should -Match "<html"
        $html | Should -Match "<head>"
        $html | Should -Match "<body>"
    }

    It "Should include Chart.js library" {
        $html = Get-Content "monitoring\dashboard_ontology.html" -Raw
        $html | Should -Match "chart\.js|Chart\.js"
    }

    It "Should have data loading functionality" {
        $html = Get-Content "monitoring\dashboard_ontology.html" -Raw
        $html | Should -Match "fetch.*ontology_audit_report\.json"
        $html | Should -Match "loadReport|load_report"
    }

    It "Should display coverage metrics" {
        $html = Get-Content "monitoring\dashboard_ontology.html" -Raw
        $html | Should -Match "coverage|Couverture"
        $html | Should -Match "matched|Matchés"
        $html | Should -Match "missing|Manquants"
    }

    It "Should have chart canvas" {
        $html = Get-Content "monitoring\dashboard_ontology.html" -Raw
        $html | Should -Match "<canvas.*coverageChart"
    }
}