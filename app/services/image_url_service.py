"""
Resolve links "de página" (ex: https://ibb.co/xxxxx, https://imgur.com/xxxxx)
para o link DIRETO da imagem (ex: https://i.ibb.co/xxxxx/foto.jpg).

Por quê: sites como Imgur e ibb.co escondem o link direto atrás de um botão
específico ("copiar endereço da imagem" / "direct link"), e é fácil colar o
link errado sem perceber (a página abre normalmente no navegador, só quebra
quando usada num <img src="...">). Em vez de depender do usuário achar o
botão certo, o backend tenta resolver isso sozinho: se o link já é uma
imagem direta, usa como está; senão, busca a página e extrai a tag
<meta property="og:image" ...>, que praticamente todo site de hospedagem de
imagem preenche com o link direto (é o mesmo link que aparece quando você
compartilha a página no WhatsApp/Twitter/etc).
"""

import html
import ipaddress
import re
import socket
from urllib.parse import urlparse

import requests

_EXTENSOES_IMAGEM = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif")
_TIMEOUT_SEGUNDOS = 5
_TAMANHO_MAXIMO_RESPOSTA = 2_000_000  # 2MB — página HTML não devia passar disso; evita baixar algo gigante

_REGEX_META_OG_IMAGE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]*>', re.IGNORECASE)
_REGEX_CONTENT_ATTR = re.compile(r'content=["\']([^"\']+)["\']', re.IGNORECASE)


def _parece_link_direto_de_imagem(url: str) -> bool:
    sem_query = url.split("?", 1)[0].split("#", 1)[0]
    return sem_query.lower().endswith(_EXTENSOES_IMAGEM)


def _host_e_seguro(url: str) -> bool:
    """
    Bloqueia URLs que resolvem para IPs privados/internos (loopback, link-local,
    faixas reservadas etc). Sem isso, um usuário autenticado poderia usar este
    campo para fazer o servidor requisitar endereços internos (SSRF).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    try:
        enderecos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        return False
    for *_, sockaddr in enderecos:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def _extrair_og_image(html_texto: str) -> str | None:
    tag_match = _REGEX_META_OG_IMAGE.search(html_texto)
    if not tag_match:
        return None
    content_match = _REGEX_CONTENT_ATTR.search(tag_match.group(0))
    if not content_match:
        return None
    return html.unescape(content_match.group(1))


def resolver_url_imagem(url: str) -> str:
    """
    Tenta transformar `url` num link direto de imagem. Se `url` já parece
    direta, retorna como está (sem gastar uma requisição HTTP à toa). Se não
    conseguir resolver por qualquer motivo (rede, site sem og:image, timeout),
    retorna a URL original sem levantar erro — o pior caso é a imagem não
    carregar no frontend, igual já acontecia antes, nunca quebra o salvamento
    do perfil.
    """
    url = url.strip()
    if not url or _parece_link_direto_de_imagem(url):
        return url

    if not _host_e_seguro(url):
        return url

    try:
        resposta = requests.get(
            url,
            timeout=_TIMEOUT_SEGUNDOS,
            headers={"User-Agent": "Mozilla/5.0 (compatible; InglesIA/1.0)"},
            stream=True,
            allow_redirects=False,
        )
        if resposta.is_redirect:
            return url
        resposta.raise_for_status()

        conteudo = b""
        for pedaco in resposta.iter_content(chunk_size=8192):
            conteudo += pedaco
            if len(conteudo) > _TAMANHO_MAXIMO_RESPOSTA:
                break

        og_image = _extrair_og_image(conteudo.decode("utf-8", errors="ignore"))
        return og_image if og_image else url
    except (requests.RequestException, UnicodeDecodeError):
        return url
