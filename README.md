# Web Crawler HTTP — Redes de Computadores

**Autor:** Gabriel Menezes de Araújo
Universidade de Brasília — Departamento de Ciência da Computação

## Sobre

Web crawler desenvolvido em Python 3 que implementa o protocolo HTTP manualmente, usando apenas `socket` para a comunicação de rede (sem `requests`, `urllib.request` ou `http.client`). O crawler conecta-se via TCP, monta requisições HTTP na mão, interpreta as respostas, segue redirecionamentos (301/302), extrai links com BeautifulSoup e gera um relatório final.

## Funcionalidades

- Requisições HTTP construídas manualmente sobre sockets TCP
- Interpretação de status code, cabeçalhos e corpo da resposta
- Extração de links via BeautifulSoup (apenas parsing, sem requisição)
- Navegação recursiva (BFS) com controle de URLs visitadas (evita loops)
- Tratamento de redirecionamentos 301/302
- Restrição de domínios permitidos (`localhost`, `127.0.0.1`, `info.cern.ch`)
- Geração de relatório (`relatorio_crawler.txt`) com estatísticas e detalhes

## Requisitos

- Python 3
- BeautifulSoup4
- Docker (opcional, para ambiente de testes local)

```bash
pip3 install beautifulsoup4
```

## Como executar

1. (Opcional) Suba o servidor de testes local:

```bash
docker run -p 80:80 robertovrf/http-crawler-lab:latest
```

Se a porta 80 estiver ocupada, use `-p 8080:80`.

2. Rode o crawler:

```bash
python3 crawler.py
```

O relatório é gerado automaticamente em `relatorio_crawler.txt`.

## Configuração

Parâmetros ajustáveis na função `main()`, na chamada de `crawlar`:

```python
crawler.crawlar('http://info.cern.ch/hypertext/WWW/TheProject.html', max_paginas=35)
```

- `url_inicial`: página de partida
- `max_paginas`: limite de páginas a visitar
- `verbose`: `False` para execução silenciosa

## Estrutura do projeto
.
├── crawler.py
├── relatorio_crawler.txt
└── README.md

## Resultados de teste

| Ambiente | Páginas visitadas | 200 | 404 | Erros |
|---|---|---|---|---|
| Docker | 28 | 22 | 4 | 2 |
| CERN | 150 | 117 | 16 | 17 |

## Referências

- Fielding, R. et al. **RFC 2616 — HTTP/1.1**. IETF, 1999.
- Python Software Foundation. **socket** — documentação oficial.
