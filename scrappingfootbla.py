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

GE_BASE = "https://ge.globo.com"

TIMES_PARA_MONITORAR = [
    {"nome": "Sao Paulo", "url": f"{GE_BASE}/futebol/times/sao-paulo/"},
    {"nome": "Palmeiras", "url": f"{GE_BASE}/futebol/times/palmeiras/"},
    {"nome": "Corinthians", "url": f"{GE_BASE}/futebol/times/corinthians/"},
    {"nome": "Santos", "url": f"{GE_BASE}/futebol/times/santos/"},
    {"nome": "Flamengo", "url": f"{GE_BASE}/futebol/times/flamengo/"},
    {"nome": "Vasco", "url": f"{GE_BASE}/futebol/times/vasco/"},
    {"nome": "Gremio", "url": f"{GE_BASE}/futebol/times/gremio/"},
    {"nome": "Internacional", "url": f"{GE_BASE}/futebol/times/internacional/"},
    {"nome": "Atletico-MG", "url": f"{GE_BASE}/futebol/times/atletico-mg/"},
    {"nome": "Cruzeiro", "url": f"{GE_BASE}/futebol/times/cruzeiro/"},
]

# A selecao brasileira tem URL propria; as demais seguem /futebol/selecoes/<slug>/
SELECOES_PARA_MONITORAR = [
    {"nome": "Brasil", "url": f"{GE_BASE}/futebol/selecao-brasileira/"},
    {"nome": "Alemanha", "url": f"{GE_BASE}/futebol/selecoes/alemanha/"},
    {"nome": "Itália", "url": f"{GE_BASE}/futebol/selecoes/italia/"},
    {"nome": "Argentina", "url": f"{GE_BASE}/futebol/selecoes/argentina/"},
    {"nome": "França", "url": f"{GE_BASE}/futebol/selecoes/franca/"},
    {"nome": "Uruguai", "url": f"{GE_BASE}/futebol/selecoes/uruguai/"},
    {"nome": "Espanha", "url": f"{GE_BASE}/futebol/selecoes/espanha/"},
    {"nome": "Inglaterra", "url": f"{GE_BASE}/futebol/selecoes/inglaterra/"},
    {"nome": "Bélgica", "url": f"{GE_BASE}/futebol/selecoes/belgica/"},
    {"nome": "Croácia", "url": f"{GE_BASE}/futebol/selecoes/croacia/"},
    {"nome": "Holanda", "url": f"{GE_BASE}/futebol/selecoes/holanda/"},
    {"nome": "Portugal", "url": f"{GE_BASE}/futebol/selecoes/portugal/"},
    {"nome": "Marrocos", "url": f"{GE_BASE}/futebol/selecoes/marrocos/"},
    {"nome": "Japão", "url": f"{GE_BASE}/futebol/selecoes/japao/"},
    {"nome": "Senegal", "url": f"{GE_BASE}/futebol/selecoes/senegal/"},
]

CATEGORIAS = {
    "times": {"rotulo": "Time", "itens": TIMES_PARA_MONITORAR},
    "selecoes": {"rotulo": "Seleção", "itens": SELECOES_PARA_MONITORAR},
}

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


def buscar_info_jogo(item):
    """Busca horario/transmissao do proximo jogo no ge.globo.com."""
    nome = item["nome"]
    url_base = item["url"]

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


def buscar_com_cache(item):
    chave = item["url"]
    agora = time.time()

    with _cache_lock:
        entrada = _cache.get(chave)
        if entrada and agora < entrada["expira_em"]:
            return entrada["resultado"]

    resultado = buscar_info_jogo(item)
    ttl = CACHE_TTL_SUCESSO if resultado["sucesso"] else CACHE_TTL_FALHA
    with _cache_lock:
        _cache[chave] = {"resultado": resultado, "expira_em": agora + ttl}
    return resultado


def _aba_valida(aba):
    return aba if aba in CATEGORIAS else "times"


def _render_pagina(aba, resultado=None, selecionado=None, status=200):
    return (
        render_template(
            "index.html",
            aba=aba,
            categorias=CATEGORIAS,
            itens=CATEGORIAS[aba]["itens"],
            rotulo=CATEGORIAS[aba]["rotulo"],
            resultado=resultado,
            selecionado=selecionado,
        ),
        status,
    )


@app.route("/", methods=["GET"])
def index():
    aba = _aba_valida(request.args.get("aba", "times"))
    return _render_pagina(aba)


@app.route("/buscar", methods=["POST"])
def buscar():
    aba = _aba_valida(request.form.get("categoria", "times"))
    nome = request.form.get("time")
    logger.info("POST /buscar - categoria: %s, nome: %s", aba, nome)

    item = next((i for i in CATEGORIAS[aba]["itens"] if i["nome"] == nome), None)
    if not item:
        return _render_pagina(
            aba,
            resultado={"sucesso": False, "mensagem": "Opcao invalida. Selecione uma opcao da lista."},
        )

    resultado = buscar_com_cache(item)
    return _render_pagina(aba, resultado=resultado, selecionado=nome)


@app.errorhandler(Exception)
def erro_inesperado(e):
    if isinstance(e, HTTPException):
        return e
    logger.exception("Erro inesperado")
    return _render_pagina(
        "times",
        resultado={"sucesso": False, "mensagem": "Erro inesperado no servidor. Tente novamente."},
        status=500,
    )


def main_scraper():
    for categoria in CATEGORIAS.values():
        for item in categoria["itens"]:
            resultado = buscar_info_jogo(item)
            if resultado["sucesso"]:
                print(f"[OK] {item['nome']}: {resultado['horario']} | {resultado['transmissao']}")
            else:
                print(f"[ERRO] {item['nome']}: {resultado['mensagem']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main_scraper()
    else:
        port = int(os.environ.get("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)
