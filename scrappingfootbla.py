import asyncio
import os
import sys
from urllib.parse import urljoin

from flask import Flask, render_template, request
from playwright.async_api import async_playwright

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

app = Flask(__name__, template_folder="templates", static_folder="static")


async def buscar_info_jogo(browser_context, time_info):
    """Processa um time por vez e retorna horario/transmissao."""
    nome = time_info["nome"]
    slug = time_info["slug"]
    page = await browser_context.new_page()
    url_base = f"https://ge.globo.com/futebol/times/{slug}/"

    try:
        await page.goto(url_base, timeout=60000)
        link_elemento = page.locator("a[href*='onde-assistir']").first

        if await link_elemento.count() == 0:
            return {
                "sucesso": False,
                "horario": None,
                "transmissao": None,
                "mensagem": "Nenhuma noticia de 'onde assistir' encontrada no momento.",
            }

        link_noticia = await link_elemento.get_attribute("href")
        if not link_noticia:
            return {
                "sucesso": False,
                "horario": None,
                "transmissao": None,
                "mensagem": "Link da noticia nao encontrado.",
            }

        await page.goto(urljoin(url_base, link_noticia), timeout=60000)

        transmissao = await page.locator("li:has-text('Transmiss')").first.inner_text()
        horario = await page.locator("li:has-text('Hor')").first.inner_text()

        return {
            "sucesso": True,
            "horario": horario.strip(),
            "transmissao": transmissao.strip(),
            "mensagem": "Informacao obtida com sucesso.",
        }
    except Exception:
        return {
            "sucesso": False,
            "horario": None,
            "transmissao": None,
            "mensagem": f"Erro ao processar {nome}. Tente novamente mais tarde.",
        }
    finally:
        await page.close()


async def buscar_info_jogo_selecionado(time_info):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        resultado = await buscar_info_jogo(context, time_info)
        await browser.close()
        return resultado


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", times=TIMES_PARA_MONITORAR, resultado=None, selecionado=None)


@app.route("/buscar", methods=["POST"])
def buscar():
    nome_time = request.form.get("time")
    time_info = next((t for t in TIMES_PARA_MONITORAR if t["nome"] == nome_time), None)

    if not time_info:
        return render_template(
            "index.html",
            times=TIMES_PARA_MONITORAR,
            resultado={"sucesso": False, "mensagem": "Time invalido. Selecione um time da lista."},
            selecionado=None,
        )

    resultado = asyncio.run(buscar_info_jogo_selecionado(time_info))
    return render_template("index.html", times=TIMES_PARA_MONITORAR, resultado=resultado, selecionado=nome_time)


async def main_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        for time in TIMES_PARA_MONITORAR:
            resultado = await buscar_info_jogo(context, time)
            if resultado["sucesso"]:
                print(f"[OK] {time['nome']}: {resultado['horario']} | {resultado['transmissao']}")
            else:
                print(f"[ERRO] {time['nome']}: {resultado['mensagem']}")
        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        asyncio.run(main_scraper())
    else:
        port = int(os.environ.get("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)
