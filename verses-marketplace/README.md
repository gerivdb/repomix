# Verses Marketplace

**Diamond Meta-Cluster Community Verse Exchange Platform**

## Overview

The Verses Marketplace enables community publishing, discovery, and evaluation of verses with automatic dependency resolution.

## API Endpoints

```
POST /verses/publish     # Publish new verse
GET  /verses/search      # Search verses by query/domain
GET  /verses/{id}        # Get verse details
GET  /verses/{id}/deps    # Resolve dependencies
POST /verses/{id}/rate   # Rate verse quality
```

## Verse Structure

```yaml
id: verse-name
name: Human Readable Name
domain: PHYSICS|MATH|AI|BIO|TECH|BATVERSE
version: 1.0.0
dependencies: [other-verse-ids]
maintainers: [team-names]
quality_score: 0-100
description: Verse description
```

## Quality Scores

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Excellent | Production ready, highly validated |
| 80-89 | Good | Stable with minor issues |
| 70-79 | Fair | Functional but needs improvement |
| 60-69 | Poor | Limited functionality |
| <60 | Critical | Broken or incomplete |

## Usage

### Publishing a Verse

```bash
curl -X POST http://localhost:3000/verses/publish \
  -H "Content-Type: application/json" \
  -d @my-verse.yaml
```

### Searching Verses

```bash
# Search by query
curl http://localhost:3000/verses/search?query=quantum

# Search by domain
curl http://localhost:3000/verses/search?domain=PHYSICS
```

### Resolving Dependencies

```bash
curl http://localhost:3000/verses/quantum-entanglement/deps
```

## Integration with Diamond Meta-Cluster

The marketplace integrates with:
- **BLO**: Event bus notifications for new verses
- **VERSUS**: Registry synchronization
- **Alphafold**: Quality prediction for submissions
- **GitNote**: Semantic enrichment of verse descriptions