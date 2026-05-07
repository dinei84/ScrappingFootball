# 📋 Guia de Deploy no Render - ScrappingFootball

## ✅ Status Atual

Seu projeto **JÁ TEM** a configuração necessária para rodar no Render. Os arquivos essenciais estão em lugar:

- ✅ `render.yaml` - Configurado
- ✅ `requirements.txt` - Configurado com todas as dependências
- ✅ `scrappingfootbla.py` - Pronto para produção

---

## 🔍 Verificação de Configurações

### 1. **render.yaml** (VERIFICAR)
```yaml
services:
  - type: web
    name: scrappingfootball
    env: python
    buildCommand: pip install -r ./requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium
    startCommand: gunicorn scrappingfootbla:app --bind 0.0.0.0:$PORT
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PLAYWRIGHT_BROWSERS_PATH
        value: /opt/render/.cache/ms-playwright
```

**Status:** ✅ CORRETO

---

### 2. **requirements.txt** (VERIFICAR)
```
Flask
playwright
gunicorn
flask-cors
```

**Status:** ✅ CORRETO

---

### 3. **Variáveis de Ambiente no Render**

Acesse: **Dashboard Render > Seu Serviço > Environment**

#### Variáveis Necessárias:

| Variável | Valor | Obrigatória? | Notas |
|----------|-------|--------------|-------|
| `FLASK_ENV` | `production` | ⚠️ Importante | Já configurado no render.yaml |
| `PYTHONUNBUFFERED` | `1` | ⚠️ Importante | Já configurado no render.yaml |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/render/.cache/ms-playwright` | ⚠️ Importante | Já configurado no render.yaml |

**Se quiser adicionar outras variáveis (futuro):**
- Clique em "Add Environment Variable"
- Key: `NOME_DA_VARIAVEL`
- Value: `seu_valor`

---

## 🚀 Processo de Deploy

### Passo 1: Verificar se o repositório está no GitHub
```bash
git remote -v
# Deve retornar algo como:
# origin  https://github.com/seu_usuario/ScrappingFootball.git (fetch)
```

### Passo 2: Fazer commit e push das mudanças
```bash
git add .
git commit -m "Fix: Configurar Playwright para produção"
git push origin main
```

### Passo 3: No Dashboard do Render
1. Acesse: https://dashboard.render.com
2. Selecione seu serviço "scrappingfootball"
3. Clique em "Manual Deploy" ou "Redeploy latest commit"
4. Aguarde o build completar (pode levar 3-5 minutos)

### Passo 4: Monitorar o Deployment
1. Vá para a aba **"Logs"** no dashboard
2. Procure por essas mensagens:
   ```
   ✅ "Flask app initialized successfully"
   ✅ "Playwright browsers installed"
   ✅ "Running on 0.0.0.0"
   ```
3. Se houver erros, estarão nos logs também

---

## ⚙️ Settings Específicas do Render

### Verificar no Dashboard (Settings > General)

| Campo | Valor Esperado | Status |
|-------|----------------|--------|
| **Name** | scrappingfootball | Seu serviço |
| **Runtime** | Python 3.x | Automático |
| **Build Command** | `pip install -r ./requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium` | ✅ Configurado |
| **Start Command** | `gunicorn scrappingfootbla:app --bind 0.0.0.0:$PORT` | ✅ Configurado |
| **Region** | `Ohio` (recomendado) ou sua preferência | Você escolhe |
| **Instance Type** | Starter ou Standard | Recomendado: Starter para teste |

---

## 🔧 Variáveis de Ambiente - Como Adicionar Novas

Se precisar adicionar outras variáveis no futuro (ex: API keys, configurações):

### No Dashboard Render:
1. Vá para **Environment** > **Add Environment Variable**
2. Preencha:
   - **Key:** Nome da variável (ex: `API_KEY`)
   - **Value:** O valor (ex: `sua-chave-aqui`)
3. Clique em **Save**
4. **Deploy novamente** para aplicar

### No Código Python:
```python
import os
api_key = os.environ.get("API_KEY", "valor_padrao")
```

---

## 🆘 Troubleshooting

### ❌ Erro: "Internal Server Error (500)"
- Verifique os logs no Render (aba "Logs")
- Certifique-se de que `render.yaml` está correto
- Re-faça o deploy: **Manual Deploy**

### ❌ Erro: "Playwright browsers not found"
- Verifique se `buildCommand` tem: `python -m playwright install chromium`
- Certifique-se de que `PLAYWRIGHT_BROWSERS_PATH` está configurado
- Re-faça o deploy

### ❌ Erro: "Module not found" (Flask, gunicorn, etc)
- Confirme que `requirements.txt` está no diretório raiz
- Verifique se todos os pacotes estão listados:
  ```
  Flask
  playwright
  gunicorn
  flask-cors
  ```
- Re-faça o deploy

### ❌ Erro: "Port already in use"
- Render usa a variável `$PORT` automaticamente
- Certifique-se de que startCommand usa: `--bind 0.0.0.0:$PORT`

---

## ✅ Checklist Pré-Deploy

- [ ] Arquivo `render.yaml` existe e está correto
- [ ] Arquivo `requirements.txt` existe e lista todas as dependências
- [ ] Código foi commitado no git: `git push origin main`
- [ ] Dashboard Render mostra as variáveis de ambiente corretas
- [ ] Histórico de logs não mostra erros de build

---

## 📊 Teste de Funcionalidade Pós-Deploy

Após o deploy estar online, teste:

1. **GET / (carregamento da página)**
   ```bash
   curl https://seu-servico.onrender.com/
   ```
   Deve retornar HTML da página

2. **POST /buscar (buscar um time)**
   ```bash
   curl -X POST https://seu-servico.onrender.com/buscar \
     -d "time=Sao Paulo"
   ```
   Deve retornar HTML com resultado (sucesso ou "não encontrado")

3. **Verifique os logs**
   - Dashboard Render > Logs
   - Procure por `INFO:__main__:POST /buscar`

---

## 📝 Notas Importantes

1. **O buildCommand é essencial:** Sem ele, Playwright não funcionará
2. **PLAYWRIGHT_BROWSERS_PATH é necessário:** Define onde os browsers serão armazenados em cache
3. **PYTHONUNBUFFERED=1 é recomendado:** Garante que logs apareçam em tempo real
4. **Gunicorn é obrigatório:** Flask dev server não é adequado para produção

---

## 🔗 Recursos Úteis

- [Render Docs - Python](https://render.com/docs/deploy-python)
- [Playwright - Environment Setup](https://playwright.dev/python/)
- [Render - Environment Variables](https://render.com/docs/environment-variables)

---

## ❓ Próximos Passos

1. Faça um **Manual Deploy** no Render
2. Monitore os **Logs** até o build completar
3. Teste a URL da sua aplicação
4. Se houver erros, volte a este guia na seção "Troubleshooting"

