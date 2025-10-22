# Melhorias de Segurança Recomendadas

## 1. Configuração de Variáveis de Ambiente
Criar arquivo `.env` para variáveis sensíveis:

```bash
# .env
GROQ_API_KEY=sua_chave_aqui
MASTER_PASSWORD=senha_forte_aqui
```

## 2. Hash de Senhas
Implementar hash das senhas usando bcrypt:

```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

## 3. Rotação de Senhas
Implementar sistema de expiração de senhas.

## 4. Logs de Segurança
Adicionar logs de tentativas de login e acessos.
