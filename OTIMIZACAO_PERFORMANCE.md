# Otimizações de Performance Recomendadas

## 1. Cache de Dados
Implementar cache para consultas à API:

```python
import streamlit as st
from functools import lru_cache
import time

@st.cache_data(ttl=3600)  # Cache por 1 hora
def consultar_api_cached(agregado):
    return consultar_api(agregado)
```

## 2. Lazy Loading
Carregar dados apenas quando necessário:

```python
def carregar_dados_sob_demanda(agregado):
    if agregado not in st.session_state.cache_dados:
        st.session_state.cache_dados[agregado] = consultar_api(agregado)
    return st.session_state.cache_dados[agregado]
```

## 3. Otimização de Visualizações
- Usar `st.empty()` para atualizações dinâmicas
- Implementar paginação para grandes datasets
- Usar `st.progress()` para feedback visual

## 4. Processamento Assíncrono
Para operações pesadas:

```python
import asyncio
import aiohttp

async def consultar_api_async(agregado):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as response:
            return await response.json()
```

## 5. Compressão de Dados
- Usar compressão gzip nas requisições
- Implementar compressão de dados no cache
