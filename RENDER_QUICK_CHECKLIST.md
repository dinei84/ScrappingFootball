# ⚡ Checklist Rápido - Deploy no Render

## 1️⃣ No seu Computador (Local)

```bash
# Faça commit das mudanças
git add .
git commit -m "Fix: Configurar Playwright para ambiente de produção"

# Envie para GitHub
git push origin main
```

---

## 2️⃣ No Dashboard do Render

### Acesse: https://dashboard.render.com

**Passo 1:** Selecione seu serviço "scrappingfootball"

**Passo 2:** Vá para a aba **"Environment"**
- Verifique se existem estas variáveis:
  - ✅ `FLASK_ENV` = `production`
  - ✅ `PYTHONUNBUFFERED` = `1`
  - ✅ `PLAYWRIGHT_BROWSERS_PATH` = `/opt/render/.cache/ms-playwright`

> **Se faltarem**, adicione clicando em "Add Environment Variable"

**Passo 3:** Vá para **"Settings"** e verifique:
- Build Command: `pip install -r ./requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium`
- Start Command: `gunicorn scrappingfootbla:app --bind 0.0.0.0:$PORT`

> **Se estiverem diferentes**, atualize e salve

**Passo 4:** Volte para a aba **"Deploy"**
- Clique em **"Manual Deploy"** ou **"Redeploy latest commit"**
- Aguarde até ver: `Your service is live 🎉`

**Passo 5:** Monitore os Logs
- Vá para a aba **"Logs"**
- Procure por:
  - ✅ `Flask app initialized successfully`
  - ✅ `Playwright browsers installed` (ou similar)
  - ❌ Se houver `Error`, algo está errado

---

## 3️⃣ Teste a Aplicação

Após o deploy estar "live", acesse:
```
https://seu-servico.onrender.com/
```

- Escolha um time
- Clique em "Buscar informação"
- Se funcionar → ✅ Tudo OK!
- Se der erro → Verifique os logs

---

## 📌 Variáveis de Ambiente - Template Completo

Se precisa adicionar manualmente todas as variáveis:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `PYTHONUNBUFFERED` | `1` |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/render/.cache/ms-playwright` |

---

## 🆘 Se Não Funcionar

1. **Verifique os Logs** no Render (aba Logs)
2. **Procure por "Error"** nos logs
3. **Copie a mensagem de erro**
4. **Re-faça o deploy** (Manual Deploy)
5. **Aguarde 3-5 minutos**

---

## ✅ Pronto?

Se todos os passos estão OK, sua aplicação deve estar funcionando em produção! 🚀

