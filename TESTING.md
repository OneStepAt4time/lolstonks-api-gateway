# Testing Guide

## TL;DR - Non serve act!

**Per testare localmente, usa questi comandi:**

```bash
# Test rapidi
make test-quick

# Test completi con coverage
make test

# Simula tutta la CI di GitHub Actions
make ci

# Quick CI (solo lint + test veloci)
make ci-quick
```

## Perché non usare act?

Act su Windows con Docker Desktop ha problemi noti:
- Conflitti di porta con servizi esistenti (Redis)
- Bug con health checks dei services
- Lentezza rispetto ai test diretti

**Soluzione:** Testa direttamente con pytest e make. È più veloce e affidabile!

## Comandi di Test Disponibili

### Test Base

```bash
# Test completi con coverage
make test
# Output: Report HTML in htmlcov/index.html

# Test veloci (senza coverage)
make test-quick

# Test specifici
uv run pytest tests/test_main.py -v
uv run pytest tests/test_config.py::test_riot_api_key_loaded -v
```

### Linting e Formattazione

```bash
# Check linting
make lint

# Auto-fix linting
make format

# Solo type checking
uv run mypy app/ --ignore-missing-imports
```

### Pre-commit Hooks

```bash
# Run tutti gli hooks
uv run pre-commit run --all-files

# Run su file specifici
uv run pre-commit run --files app/main.py
```

### CI Locale (Simula GitHub Actions)

```bash
# Full CI pipeline (lint + test + docs)
make ci

# Quick check (solo lint + test)
make ci-quick
```

## Test Workflow

### Workflow Raccomandato Durante Sviluppo

```bash
# 1. Fai le tue modifiche
vim app/main.py

# 2. Format e lint
make format

# 3. Test rapidi
make test-quick

# 4. Prima di committare
make ci-quick
```

### Prima di Push

```bash
# Esegui tutta la CI
make ci

# Gli hooks pre-commit gireranno automaticamente
git commit -m "feat: your changes"
```

## Coverage Report

Dopo `make test`, apri il report:

```bash
# Windows
start htmlcov/index.html

# Linux/macOS
open htmlcov/index.html
```

## Test con Redis

I test usano il Redis del tuo `docker-compose.yml` (porta 6379).

**Assicurati che Redis sia running:**

```bash
docker-compose up -d redis
# oppure
make docker-run
```

## Debugging Tests

### Test Singolo in Verbose

```bash
uv run pytest tests/test_main.py::test_health_endpoint -vv
```

### Con breakpoint

```python
def test_something():
    import pdb; pdb.set_trace()
    # your test code
```

```bash
uv run pytest tests/test_main.py::test_something -s
```

### Con output print

```bash
uv run pytest tests/test_main.py -s -v
```

## Continuous Testing (Watch Mode)

Per test automatici durante sviluppo:

```bash
# Installa pytest-watch
uv pip install pytest-watch

# Run in watch mode
uv run ptw -- -v
```

## GitHub Actions

La vera CI gira su GitHub quando fai push o apri PR.

**Check status:**
- Vai su: https://github.com/OneStepAt4time/lolstonks-api-gateway/actions

## Troubleshooting

### Port 6379 già in uso

```bash
# Check cosa usa la porta
docker ps --filter "publish=6379"

# Se necessario, restart Redis
docker-compose restart redis
```

### Test falliscono per Redis connection

```bash
# Verifica Redis sia up
docker-compose ps redis

# Check logs
docker-compose logs redis
```

### Coverage non si genera

```bash
# Clean e retry
make clean
make test
```

### Pre-commit troppo lento

```bash
# Skip temporaneamente (emergenze only!)
git commit --no-verify -m "message"
```

## Comandi Makefile - Reference Rapido

| Comando | Descrizione |
|---------|-------------|
| `make test` | Test con coverage completa |
| `make test-quick` | Test veloci senza coverage |
| `make lint` | Controlla linting |
| `make format` | Formatta codice |
| `make ci` | Full CI locale |
| `make ci-quick` | Quick CI check |
| `make run` | Avvia dev server |
| `make docker-run` | Avvia Docker services |
| `make clean` | Pulisci file generati |

## Summary

**Non perdere tempo con act su Windows!**

Usa invece:
1. `make test` per test locali
2. `make ci` per simulare GitHub Actions
3. GitHub Actions per CI ufficiale

È più veloce, più affidabile e senza problemi! ✅
