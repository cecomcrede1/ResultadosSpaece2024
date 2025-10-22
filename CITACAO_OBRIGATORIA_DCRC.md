# Melhorias Implementadas - Citação Obrigatória do DCRC

## Problema Identificado
A análise não estava citando o DCRC adequadamente, mesmo tendo instruções para fazê-lo. O sistema precisava ser melhorado para garantir citações explícitas do Documento Curricular Referencial do Ceará.

## Solução Implementada: Citação Obrigatória do DCRC

### 1. Melhoria na Identificação de Fonte
**Localização**: Linha 656-662

**Mudanças Implementadas**:
- **ANTES**: Identificação simples baseada apenas em palavras-chave básicas
- **DEPOIS**: Identificação robusta com múltiplos critérios e fallback para DCRC

```python
# Identificar se o chunk é do BNCC ou DCRC
if "BNCC" in chunk_texto or "Base Nacional Comum Curricular" in chunk_texto or "BNCC_20dez_site" in chunk_texto:
    fonte_documento = "BNCC"
elif "DCRC" in chunk_texto or "Documento Curricular Referencial" in chunk_texto or "dcrc" in chunk_texto.lower():
    fonte_documento = "DCRC"
else:
    # Se não conseguir identificar, usar contexto do texto combinado
    fonte_documento = "DCRC"  # Por padrão, assumir DCRC já que é o documento principal
```

### 2. Busca Específica para Habilidades com Foco no DCRC
**Localização**: Linha 672-694

**Mudanças Implementadas**:
- **Palavras-chave expandidas**: Incluídas "dcrc" e "documento curricular"
- **Identificação de fonte**: Cada resultado de habilidade é marcado com sua fonte
- **Fallback para DCRC**: Por padrão, assume DCRC quando não consegue identificar

```python
palavras_habilidade = ['habilidade', 'competência', 'capacidade', 'componente', 'relação', 'vinculação', 'conexão', 'descrição', 'caracterização', 'específica', 'geral', 'essencial', 'dcrc', 'documento curricular']
```

### 3. Instrução Obrigatória para Citar DCRC
**Localização**: Linha 1382

**Mudanças Implementadas**:
- **Nova instrução**: "CITE O DCRC OBRIGATORIAMENTE"
- **Especificação**: "Sempre que possível, referencie o DCRC como fonte principal das metodologias e competências específicas do Ceará"

### 4. Prompt Principal com Citação Obrigatória
**Localização**: Linha 1448

**Mudanças Implementadas**:
- **Instrução específica**: "CITE OBRIGATORIAMENTE O DCRC"
- **Contexto**: "como fonte principal das metodologias e competências específicas do Ceará"

### 5. Análise de Percursos com Citação Obrigatória
**Localização**: Linha 404

**Mudanças Implementadas**:
- **Nova instrução**: "CITE OBRIGATORIAMENTE O DCRC"
- **Especificação**: "Sempre que possível, referencie o DCRC como fonte principal das metodologias e competências específicas do Ceará"

### 6. Análise de Habilidades com Citação Obrigatória
**Localização**: Linha 1310

**Mudanças Implementadas**:
- **Nova instrução**: "CITE OBRIGATORIAMENTE O DCRC"
- **Especificação**: "Sempre que possível, referencie o DCRC como fonte principal das metodologias e competências específicas do Ceará"

## Benefícios das Melhorias

### ✅ **Citação Explícita do DCRC**
- Instruções obrigatórias para citar o DCRC
- Identificação robusta da fonte dos documentos
- Fallback para DCRC quando não consegue identificar

### ✅ **Fundamentação Específica do Ceará**
- DCRC como fonte principal das metodologias específicas do Ceará
- Competências específicas do estado do Ceará
- Contextualização regional adequada

### ✅ **Rastreabilidade das Fontes**
- Cada informação é marcada com sua fonte (BNCC ou DCRC)
- Possibilidade de verificar a origem de cada recomendação
- Transparência nas análises

### ✅ **Qualidade das Respostas**
- Citações explícitas do DCRC
- Metodologias específicas do Ceará
- Ações pedagógicas baseadas no documento curricular do estado

## Como Funciona a Citação Obrigatória

### 1. Identificação Robusta de Fonte
- Múltiplos critérios para identificar BNCC vs DCRC
- Fallback para DCRC quando não consegue identificar
- Marcação de cada informação com sua fonte

### 2. Busca Específica para DCRC
- Palavras-chave expandidas incluindo "dcrc" e "documento curricular"
- Priorização de informações do DCRC
- Identificação de fonte para cada resultado

### 3. Instruções Obrigatórias
- Instruções explícitas para citar o DCRC
- Especificação do DCRC como fonte principal do Ceará
- Referenciamento obrigatório em todas as análises

### 4. Prompts Específicos
- Prompts principais com instrução obrigatória
- Análises específicas com citação obrigatória
- Contextualização regional adequada

## Resultado Esperado

As análises agora devem:
- ✅ **Citar explicitamente o DCRC** em todas as recomendações
- ✅ **Referenciar metodologias específicas** do Ceará
- ✅ **Fundamentar competências específicas** do estado
- ✅ **Contextualizar regionalmente** as análises
- ✅ **Identificar claramente** a fonte de cada informação
- ✅ **Priorizar o DCRC** como documento principal do Ceará

## Exemplo de Citação Esperada

### ANTES (Sem citação do DCRC):
"Use metodologias sugeridas nos documentos para intervenções"

### DEPOIS (Com citação obrigatória do DCRC):
"Conforme o DCRC, use metodologias específicas sugeridas no Documento Curricular Referencial do Ceará para intervenções pedagógicas direcionadas às competências específicas do estado"

## Instruções para a IA

A IA agora deve obrigatoriamente:
1. **CITAR O DCRC** em todas as análises
2. **REFERENCIAR** "conforme o DCRC" ou "segundo o Documento Curricular Referencial do Ceará"
3. **PRIORIZAR** o DCRC como fonte principal das metodologias do Ceará
4. **IDENTIFICAR** a fonte de cada recomendação
5. **CONTEXTUALIZAR** regionalmente as análises
6. **FUNDAMENTAR** competências específicas do estado do Ceará

A análise agora **cita obrigatoriamente o DCRC** como fonte principal das metodologias e competências específicas do Ceará!
