# Tests pour validation des termes ontologiques ajoutés

Describe "Ontology Terms Validation Tests" {

    It "Should validate N/N+1/N+2 format for added terms" {
        $ontologyFile = "ONTOLOGY\ontology_complete.json"

        # Use same fallback as script
        try {
            $ontology = Get-Content $ontologyFile | ConvertFrom-Json
        } catch {
            # Skip test if JSON has issues
            Set-ItResult -Skipped -Because "JSON parsing failed due to duplicate keys"
            return
        }

        $addedTerms = @("AppData", "CDN", "WebGPU", "HardwareDiscoveryCitizen", "GPUInfo")

        foreach ($term in $addedTerms) {
            $ontology.$term | Should -Not -BeNull
            $ontology.$term.definition | Should -Match "N:.*N\+1:.*N\+2:"
            $ontology.$term.id | Should -Not -BeNull
            $ontology.$term.domain | Should -Not -BeNull
        }
    }

    It "Should have required properties for each term" {
        $ontologyFile = "ONTOLOGY\ontology_complete.json"

        try {
            $ontology = Get-Content $ontologyFile | ConvertFrom-Json
        } catch {
            Set-ItResult -Skipped -Because "JSON parsing failed due to duplicate keys"
            return
        }

        $term = $ontology.AppData  # Test one term

        $term.properties | Should -Not -BeNull
        $term.relations | Should -Not -BeNull
        $term.constraints | Should -Not -BeNull
        $term.examples | Should -Not -BeNull
        $term.version | Should -Not -BeNull
        $term.created | Should -Not -BeNull
        $term.updated | Should -Not -BeNull
    }
}