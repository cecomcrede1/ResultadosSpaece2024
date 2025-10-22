# Guia de Deploy e Configuração

## 1. Configuração de Ambiente

### Variáveis de Ambiente
Criar arquivo `.env`:

```bash
# API Keys
GROQ_API_KEY=sua_chave_groq_aqui

# Senhas (usar hash)
MASTER_PASSWORD_HASH=$2b$12$hash_aqui

# Configurações da API
SPAECE_API_URL=https://avaliacaoemonitoramentoceara.caeddigital.net/portal/functions/getDadosResultado

# Configurações de Cache
CACHE_TTL=3600
MAX_CACHE_SIZE=1000
```

### Docker
Criar `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  spaece-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./.streamlit:/app/.streamlit
    restart: unless-stopped
```

## 2. Deploy em Produção

### Streamlit Cloud
1. Conectar repositório GitHub
2. Configurar variáveis de ambiente
3. Deploy automático

### AWS/GCP/Azure
1. Usar containers
2. Configurar load balancer
3. Implementar monitoramento

## 3. Monitoramento
- Logs de acesso
- Métricas de performance
- Alertas de erro
- Backup de dados
