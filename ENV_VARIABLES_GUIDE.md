# 🔐 Guia Completo - Variáveis de Ambiente

## 📍 Onde Configurar

### No Render Dashboard:
1. Acesse: **https://dashboard.render.com**
2. Selecione seu serviço: **scrappingfootball**
3. Clique em: **Environment** (na aba de navegação superior)

---

## 📋 Variáveis Necessárias

### Para o Playwright Funcionar (OBRIGATÓRIAS)

#### 1. FLASK_ENV
```
Key:   FLASK_ENV
Value: production
```
**O que faz:** Define o Flask em modo produção (desativa debug, ativa otimizações)
**Padrão:** Já configurado no `render.yaml`

---

#### 2. PYTHONUNBUFFERED
```
Key:   PYTHONUNBUFFERED
Value: 1
```
**O que faz:** Python não buffering (os logs aparecem em tempo real)
**Padrão:** Já configurado no `render.yaml`

---

#### 3. PLAYWRIGHT_BROWSERS_PATH
```
Key:   PLAYWRIGHT_BROWSERS_PATH
Value: /opt/render/.cache/ms-playwright
```
**O que faz:** Define onde o Playwright armazena os browsers em cache
**Padrão:** Já configurado no `render.yaml`

---

## 🎯 Configuração Passo a Passo

### Se as Variáveis NÃO estão configuradas:

**Passo 1:** No dashboard Render, vá para **Environment**

**Passo 2:** Clique em **Add Environment Variable**

**Passo 3:** Preencha:
```
Key:   FLASK_ENV
Value: production
```
Clique em **Save**

**Passo 4:** Repita para as outras variáveis:
- `PYTHONUNBUFFERED` = `1`
- `PLAYWRIGHT_BROWSERS_PATH` = `/opt/render/.cache/ms-playwright`

**Passo 5:** Clique em **Deploy** para aplicar as mudanças

---

## 🔍 Como Verificar se Está Correto

### No Dashboard Render:

1. Vá para **Environment**
2. Você deve ver estas variáveis listadas:
   ```
   ✅ FLASK_ENV = production
   ✅ PYTHONUNBUFFERED = 1
   ✅ PLAYWRIGHT_BROWSERS_PATH = /opt/render/.cache/ms-playwright
   ```

### Verifique nos Logs:

1. Vá para a aba **Logs**
2. Procure por:
   ```
   INFO:__main__:Flask app initialized successfully
   ```
3. Se aparecer, as variáveis estão sendo lidas corretamente

---

## 📊 Tabela de Referência

| Nome | Valor | Tipo | Obrigatório | Onde Definir |
|------|-------|------|-------------|--------------|
| FLASK_ENV | production | String | ✅ Sim | `render.yaml` ou Environment |
| PYTHONUNBUFFERED | 1 | String/Number | ✅ Sim | `render.yaml` ou Environment |
| PLAYWRIGHT_BROWSERS_PATH | /opt/render/.cache/ms-playwright | String | ✅ Sim | `render.yaml` ou Environment |

---

## ⚠️ Erros Comuns

### ❌ Erro: "Playwright browsers not found"
**Causa:** Falta a variável `PLAYWRIGHT_BROWSERS_PATH`
**Solução:** Adicione ou verifique se está com o valor correto

### ❌ Erro: "Internal Server Error"
**Causa:** `FLASK_ENV` não está configurado como `production`
**Solução:** Verifique e corrija o valor no Environment

### ❌ Logs não aparecem em tempo real
**Causa:** `PYTHONUNBUFFERED` não está configurado
**Solução:** Adicione `PYTHONUNBUFFERED = 1` ao Environment

---

## 🔧 Variáveis Opcionais (Futuro)

Se precisar adicionar mais variáveis no futuro (ex: API keys, senhas):

**Exemplo 1: Adicionar uma API Key**
```
Key:   EXTERNAL_API_KEY
Value: sua-chave-secreta-aqui
```

**Exemplo 2: Adicionar uma URL de Banco de Dados**
```
Key:   DATABASE_URL
Value: postgresql://usuario:senha@host:5432/banco
```

**No código Python, acesse assim:**
```python
import os

api_key = os.environ.get("EXTERNAL_API_KEY")
db_url = os.environ.get("DATABASE_URL")
```

---

## 💾 Template para Copiar/Colar

Se preferir, aqui está o template com todas as variáveis:

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

---

## ✅ Checklist Final

- [ ] Abri o Dashboard Render
- [ ] Acessei a aba "Environment"
- [ ] Verifiquei se as 3 variáveis existem
- [ ] Se faltasse alguma, adicionei
- [ ] Cliquei em "Deploy" para aplicar
- [ ] Aguardei o deployment completar
- [ ] Verifiquei nos Logs se há erros

---

## 📞 Precisando de Ajuda?

Se não conseguir configurar:
1. Verifique este guia novamente
2. Consulte o guia completo: `RENDER_DEPLOYMENT_GUIDE.md`
3. Veja a seção "Troubleshooting" no guia completo

