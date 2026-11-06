"""Funções que conversam com a API pública do IBGE.

Ficam separadas das views para poderem ser usadas em mais de um lugar
(na view de municípios e na validação do serializer de AreaEntrega).
"""
import requests

URL_BASE = 'https://servicodados.ibge.gov.br/api/v1/localidades'

# Tempo máximo (em segundos) esperando o IBGE responder.
# Sem timeout, se o IBGE travar, a nossa API também ficaria travada esperando.
TIMEOUT = 10

# Siglas válidas das 27 unidades da federação
UFS_VALIDAS = {
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
    'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
}


class IBGEIndisponivel(Exception):
    """Lançada quando o IBGE está fora do ar, demora demais ou responde com erro."""


def _get(url):
    try:
        resposta = requests.get(url, timeout=TIMEOUT)
        resposta.raise_for_status()  # gera erro se o status for 4xx/5xx
        return resposta.json()
    except (requests.RequestException, ValueError) as erro:
        # RequestException cobre: timeout, sem conexão, status de erro...
        # ValueError cobre: resposta que não é JSON
        raise IBGEIndisponivel(str(erro)) from erro


def listar_municipios(uf):
    """Devolve a lista simplificada [{codigo_ibge, nome}, ...] de uma UF."""
    dados = _get(f'{URL_BASE}/estados/{uf}/municipios')
    # O IBGE devolve muita coisa (microrregião, mesorregião, região...).
    # Aqui pegamos só o que interessa para o cliente.
    return [{'codigo_ibge': m['id'], 'nome': m['nome']} for m in dados]


def municipio_existe(codigo_ibge):
    """True se o código existe no IBGE. Para código inexistente o IBGE devolve []."""
    dados = _get(f'{URL_BASE}/municipios/{codigo_ibge}')
    return bool(dados)
