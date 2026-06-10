import os
import sys
import time
import logging
import threading
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TIMES_PARA_MONITORAR = [
    {"nome": "Sao Paulo", "slug": "sao-paulo"},
    {"nome": "Palmeiras", "slug": "palmeiras"},
    {"nome": "Corinthians", "slug": "corinthians"},
    {"nome": "Santos", "slug": "santos"},
    {"nome": "Flamengo", "slug": "flamengo"},
    {"nome": "Vasco", "slug": "vasco"},
    {"nome": "Gremio", "slug": "gremio"},
    {"nome": "Internacional", "slug": "internacional"},
    {"nome": "Atletico-MG", "slug": "atletico-mg"},
    {"nome": "Cruzeiro", "slug": "cruzeiro"},
]

REQUEST_TIMEOUT = 15  # segundos por requisicao HTTP
CACHE_TTL_SUCESSO = 600  # 10 min: resultado valido muda pouco ao longo do dia
CACHE_TTL_FALHA = 60  # 1 min: evita martelar o site quando algo falha

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

_session = requests.Session()
_session.headers.update(HEADERS)

_cache = {}
_cache_lock = threading.Lock()


def _primeiro_li_contendo(soup, termos):
    """Retorna o texto do primeiro <li> cujo conteudo contenha um dos termos."""
    for li in soup.find_all("li"):
        texto = li.get_text(" ", strip=True)
        texto_lower = texto.lower()
        if any(termo in texto_lower for termo in termos):
            return texto
    return None


def buscar_info_jogo(time_info):
    """Busca horario/transmissao do proximo jogo do time no ge.globo.com."""
    nome = time_info["nome"]
    slug = time_info["slug"]
    url_base = f"https://ge.globo.com/futebol/times/{slug}/"

    try:
        resposta = _session.get(url_base, timeout=REQUEST_TIMEOUT)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")

        link_elemento = soup.select_one("a[href*='onde-assistir']")
        if not link_elemento or not link_elemento.get("href"):
            return {
                "sucesso": False,
                "horario": None,
                "transmissao": None,
                "mensagem": "Nenhuma noticia de 'onde assistir' encontrada no momento.",
            }

        url_noticia = urljoin(url_base, link_elemento["href"])
        resposta = _session.get(url_noticia, timeout=REQUEST_TIMEOUT)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")

        # O corpo da noticia lista horario e transmissao em itens <li>
        artigo = soup.select_one(".mc-article-body") or soup
        transmissao = _primeiro_li_contendo(artigo, ("transmiss",))
        horario = _primeiro_li_contendo(artigo, ("horário", "horario", "hora:"))

        if not transmissao and not horario:
            return {
                "sucesso": False,
                "horario": None,
                "transmissao": None,
                "mensagem": "Noticia encontrada, mas sem horario/transmissao no formato esperado.",
            }

        return {
            "sucesso": True,
            "horario": horario,
            "transmissao": transmissao,
            "mensagem": "Informacao obtida com sucesso.",
        }
    except requests.RequestException:
        logger.exception("Erro de rede ao processar %s", nome)
        return {
            "sucesso": False,
            "horario": None,
            "transmissao": None,
            "mensagem": f"Erro ao processar {nome}. Tente novamente mais tarde.",
        }


def buscar_com_cache(time_info):
    slug = time_info["slug"]
    agora = time.time()

    with _cache_lock:
        entrada = _cache.get(slug)
        if entrada and agora < entrada["expira_em"]:
            return entrada["resultado"]

    resultado = buscar_info_jogo(time_info)
    ttl = CACHE_TTL_SUCESSO if resultado["sucesso"] else CACHE_TTL_FALHA
    with _cache_lock:
        _cache[slug] = {"resultado": resultado, "expira_em": agora + ttl}
    return resultado


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", times=TIMES_PARA_MONITORAR, resultado=None, selecionado=None)


@app.route("/buscar", methods=["POST"])
def buscar():
    nome_time = request.form.get("time")
    logger.info("POST /buscar - time: %s", nome_time)
    time_info = next((t for t in TIMES_PARA_MONITORAR if t["nome"] == nome_time), None)

    if not time_info:
        return render_template(
            "index.html",
            times=TIMES_PARA_MONITORAR,
            resultado={"sucesso": False, "mensagem": "Time invalido. Selecione um time da lista."},
            selecionado=None,
        )

    resultado = buscar_com_cache(time_info)
    return render_template("index.html", times=TIMES_PARA_MONITORAR, resultado=resultado, selecionado=nome_time)


@app.errorhandler(Exception)
def erro_inesperado(e):
    if isinstance(e, HTTPException):
        return e
    logger.exception("Erro inesperado")
    return (
        render_template(
            "index.html",
            times=TIMES_PARA_MONITORAR,
            resultado={"sucesso": False, "mensagem": "Erro inesperado no servidor. Tente novamente."},
            selecionado=None,
        ),
        500,
    )


def main_scraper():
    for time_info in TIMES_PARA_MONITORAR:
        resultado = buscar_info_jogo(time_info)
        if resultado["sucesso"]:
            print(f"[OK] {time_info['nome']}: {resultado['horario']} | {resultado['transmissao']}")
        else:
            print(f"[ERRO] {time_info['nome']}: {resultado['mensagem']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main_scraper()
    else:
        port = int(os.environ.get("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)
