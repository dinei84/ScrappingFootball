# Scrapping Football

Projeto simples em Python para monitorar informações de jogos de times de futebol usando Flask, `requests` e BeautifulSoup.

## Dependências

Instale as dependências usando o `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

### Bibliotecas principais

- `Flask` - para rodar a interface web
- `requests` + `beautifulsoup4` - para buscar e extrair as informações do ge.globo.com
- `gunicorn` - servidor de produção usado no Render

> **Nota:** o projeto não usa mais Playwright. As páginas do ge.globo.com são renderizadas no servidor, então uma requisição HTTP simples é suficiente — o que torna a aplicação muito mais leve, rápida e compatível com o Render sem dependências de navegador.

## Como usar localmente

### 1. Rodar a aplicação web

```bash
python scrappingfootbla.py
```

Abrir no navegador:

```bash
http://localhost:5000
```

### 2. Rodar o scraper via linha de comando

```bash
python scrappingfootbla.py --cli
```

Isso executa a coleta para todos os times definidos em `TIMES_PARA_MONITORAR` e imprime os resultados no terminal.

## Deploy no Render

O projeto está preparado para deploy no Render:

- `render.yaml` descreve o serviço Web (build e start commands).
- `scrappingfootbla.py` usa `PORT` via `os.environ.get("PORT", "5000")`.

### Configuração recomendada no Render

1. No painel do Render, crie um novo serviço `Web Service`.
2. Conecte ao repositório.
3. Caso use o `render.yaml`, o Render lerá estas configurações automaticamente.
4. Se configurar manualmente, use:
   - `Build Command`: `pip install -r requirements.txt`
   - `Start Command`: `gunicorn scrappingfootbla:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`
5. Variáveis de ambiente (opcional):
   - `FLASK_ENV=production`
   - `PYTHONUNBUFFERED=1`

### Performance

- Os resultados são cacheados em memória por 10 minutos por time (1 minuto em caso de falha), evitando requisições repetidas ao ge.globo.com.
- O gunicorn roda com 2 workers e 4 threads cada, permitindo requisições concorrentes.
