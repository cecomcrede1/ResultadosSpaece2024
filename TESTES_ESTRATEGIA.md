# Estratégia de Testes Recomendada

## 1. Testes Unitários

### Estrutura de Testes
```
tests/
├── __init__.py
├── conftest.py
├── test_auth/
│   ├── __init__.py
│   ├── test_authentication.py
│   └── test_security.py
├── test_api/
│   ├── __init__.py
│   ├── test_spaece_client.py
│   └── test_data_processor.py
├── test_visualization/
│   ├── __init__.py
│   ├── test_charts.py
│   └── test_dashboard.py
└── test_ai/
    ├── __init__.py
    ├── test_groq_client.py
    └── test_rag_processor.py
```

### Exemplo de Teste
```python
import pytest
from app.auth.authentication import verify_password, hash_password

def test_password_hashing():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
```

## 2. Testes de Integração

### Teste da API
```python
import pytest
from app.api.spaece_client import consultar_api

def test_api_consulta():
    resultado = consultar_api("23")
    assert resultado is not None
    assert "data" in resultado
```

## 3. Testes E2E

### Usando Playwright
```python
import pytest
from playwright.sync_api import sync_playwright

def test_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8501")
        
        # Testar login
        page.fill("input[placeholder*='Código']", "23")
        page.fill("input[type='password']", "senha")
        page.click("button[type='submit']")
        
        # Verificar sucesso
        assert page.locator("text=Login realizado com sucesso").is_visible()
```

## 4. CI/CD Pipeline

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
```

## 5. Cobertura de Código
```bash
pip install pytest-cov
pytest --cov=app tests/
```
