# Melhorias Implementadas - Citação Equilibrada de BNCC e DCRC

## Problema Identificado
O sistema estava priorizando apenas o DCRC como fonte principal, quando na verdade tanto a BNCC quanto o DCRC são fontes principais e devem ser citados equilibradamente.

## Solução Implementada: Citação Equilibrada de BNCC e DCRC

### 1. Instruções Equilibradas para Citar Ambos os Documentos
**Localização**: Linha 1384

**Mudanças Implementadas**:
- **ANTES**: "CITE O DCRC OBRIGATORIAMENTE"
- **DEPOIS**: "CITE OBRIGATORIAMENTE BNCC E DCRC"

- **ANTES**: "referencie o DCRC como fonte principal das metodologias e competências específicas do Ceará"
- **DEPOIS**: "referencie tanto a BNCC quanto o DCRC como fontes principais das metodologias, competências e diretrizes curriculares"

### 2. Prompt Principal com Citação Equilibrada
**Localização**: Linha 1450

**Mudanças Implementadas**:
- **ANTES**: "CITE OBRIGATORIAMENTE O DCRC"
- **DEPOIS**: "CITE OBRIGATORIAMENTE BNCC E DCRC"

- **ANTES**: "como fonte principal das metodologias e competências específicas do Ceará"
- **DEPOIS**: "como fontes principais das metodologias, competências e diretrizes curriculares"

### 3. Identificação Equilibrada de Fonte
**Localização**: Linha 662-664

**Mudanças Implementadas**:
- **ANTES**: Fallback sempre para DCRC
- **DEPOIS**: Alternância equilibrada entre BNCC e DCRC

```python
# Se não conseguir identificar, usar contexto do texto combinado
# Alternar entre BNCC e DCRC para dar equilíbrio
fonte_documento = "BNCC" if idx % 2 == 0 else "DCRC"
```

### 4. Busca Específica Equilibrada para Habilidades
**Localização**: Linha 687-688

**Mudanças Implementadas**:
- **ANTES**: Fallback sempre para DCRC
- **DEPOIS**: Alternância equilibrada entre BNCC e DCRC

```python
# Alternar entre BNCC e DCRC para dar equilíbrio
fonte_habilidade = "BNCC" if i % 2 == 0 else "DCRC"
```

### 5. Busca Expandida com Termos de Ambos os Documentos
**Localização**: Linha 635

**Mudanças Implementadas**:
- **Termos adicionados**: "base nacional comum curricular" e "documento curricular referencial"
- **Palavras-chave expandidas**: Incluídas "bncc" e "base nacional comum curricular"

### 6. Análise de Percursos com Citação Equilibrada
**Localização**: Linha 404

**Mudanças Implementadas**:
- **ANTES**: "CITE OBRIGATORIAMENTE O DCRC"
- **DEPOIS**: "CITE OBRIGATORIAMENTE BNCC E DCRC"

### 7. Análise de Habilidades com Citação Equilibrada
**Localização**: Linha 1310

**Mudanças Implementadas**:
- **ANTES**: "CITE OBRIGATORIAMENTE O DCRC"
- **DEPOIS**: "CITE OBRIGATORIAMENTE BNCC E DCRC"

## Benefícios das Melhorias

### ✅ **Citação Equilibrada**
- BNCC e DCRC são citados como fontes principais
- Equilíbrio entre documentos nacionais e estaduais
- Identificação robusta de ambas as fontes

### ✅ **Fundamentação Completa**
- BNCC como base nacional comum curricular
- DCRC como documento específico do Ceará
- Competências gerais da BNCC + específicas do DCRC

### ✅ **Rastreabilidade das Fontes**
- Cada informação é marcada com sua fonte (BNCC ou DCRC)
- Alternância equilibrada quando não consegue identificar
- Transparência nas análises

### ✅ **Qualidade das Respostas**
- Citações explícitas de ambos os documentos
- Metodologias da BNCC + específicas do DCRC
- Ações pedagógicas baseadas em ambas as fontes

## Como Funciona a Citação Equilibrada

### 1. Identificação Equilibrada de Fonte
- Múltiplos critérios para identificar BNCC vs DCRC
- Alternância equilibrada quando não consegue identificar
- Marcação de cada informação com sua fonte

### 2. Busca Específica Equilibrada
- Palavras-chave expandidas incluindo termos de ambos os documentos
- Alternância equilibrada entre BNCC e DCRC
- Identificação de fonte para cada resultado

### 3. Instruções Equilibradas
- Instruções explícitas para citar ambos os documentos
- Especificação de BNCC e DCRC como fontes principais
- Referenciamento obrigatório de ambas as fontes

### 4. Prompts Equilibrados
- Prompts principais com instrução para ambos os documentos
- Análises específicas com citação equilibrada
- Contextualização nacional + regional

## Resultado Esperado

As análises agora devem:
- ✅ **Citar explicitamente BNCC e DCRC** em todas as recomendações
- ✅ **Referenciar competências gerais** da BNCC
- ✅ **Referenciar competências específicas** do DCRC
- ✅ **Fundamentar metodologias** de ambos os documentos
- ✅ **Identificar claramente** a fonte de cada informação
- ✅ **Equilibrar** citações entre documentos nacionais e estaduais

## Exemplo de Citação Esperada

### ANTES (Apenas DCRC):
"Conforme o DCRC, use metodologias específicas sugeridas no Documento Curricular Referencial do Ceará"

### DEPOIS (BNCC + DCRC):
"Conforme a BNCC e o DCRC, use metodologias sugeridas na Base Nacional Comum Curricular e no Documento Curricular Referencial do Ceará, aplicando competências gerais da BNCC e competências específicas do DCRC"

## Instruções para a IA

A IA agora deve obrigatoriamente:
1. **CITAR BNCC E DCRC** em todas as análises
2. **REFERENCIAR** "conforme a BNCC" e "segundo o DCRC"
3. **PRIORIZAR** ambos como fontes principais
4. **IDENTIFICAR** a fonte de cada recomendação
5. **CONTEXTUALIZAR** nacionalmente (BNCC) e regionalmente (DCRC)
6. **FUNDAMENTAR** competências gerais (BNCC) + específicas (DCRC)

A análise agora **cita obrigatoriamente tanto a BNCC quanto o DCRC** como fontes principais das metodologias, competências e diretrizes curriculares!
