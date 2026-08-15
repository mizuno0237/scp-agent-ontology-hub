# Public vs internal

This GitHub repo is a **sanitized public slice**.

**Never publish**

- Private container registries or internal hostnames
- Server / production compose files
- `.env` files with real secrets
- Real customer master data (named plants, live POs, client brands)
- A GitLab `--mirror` of the internal ontology hub

**OK to publish**

- Architecture and ontology building blocks
- Synthetic supply-chain samples
- A rewritten FastAPI + React runtime that loads those samples
- Synthetic ontology mapping (object / link / logic / action)

**Scan before every push**

```bash
python scripts/scan-secrets.py
```
