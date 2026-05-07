# Verses Marketplace - API Specification

## Endpoints

### Publication
```
POST /api/v1/verses/publish
{
  "name": "string",
  "domain": "PHYSICS|MATH|SCIENCE|AI|BIO|TECH",
  "content": "yaml_content",
  "author": "user_id"
}
```

### Recherche
```
GET /api/v1/verses/search?domain=PHYSICS&limit=20
```

### Rating
```
POST /api/v1/verses/{id}/rate
{
  "score": 1-5,
  "comment": "optional"
}
```

### Versions
```
GET /api/v1/verses/{id}/versions
```

## Response Format

```json
{
  "id": "VERSE-UUID",
  "name": "Nom du verse",
  "domain": "PHYSICS",
  "qualityScore": 87.5,
  "downloads": 142,
  "rating": 4.3
}
```