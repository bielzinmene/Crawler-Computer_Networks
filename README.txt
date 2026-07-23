================================================================================
WEB CRAWLER - TRABALHO REDES DE COMPUTADORES
================================================================================

Gabriel Menezes de Araújo - 241020803

================================================================================
O QUE É
================================================================================

Um crawler que navega por páginas web usando HTTP puro - sem usar bibliotecas
como requests. Ele começa numa página pre-definida, pega os links, visita cada uma e repete
o processo.

As requisições são feitas com sockets TCP e as respostas são interpretadas
manualmente.

================================================================================
O QUE PRECISA TER INSTALADO
================================================================================

- Python 3 (qualquer versão recente)
- BeautifulSoup4 (pip install beautifulsoup4)
- Docker (se quiser testar no servidor local)

================================================================================
COMO RODAR
================================================================================

1. Primeiro, instalar o BeautifulSoup:
   pip3 install beautifulsoup4

2. Para testar com o servidor local (Docker), abre um terminal e roda:
   docker run -p 80:80 robertovrf/http-crawler-lab:latest

   Se der erro de porta ocupada, usa 8080:
   docker run -p 8080:80 robertovrf/http-crawler-lab:latest

3. Em outro terminal, na pasta do crawler, executa:
   python3 crawler.py

O programa vai gerar um arquivo relatorio_crawler.txt com os resultados.

================================================================================
COMO MUDAR AS CONFIGURAÇÕES
================================================================================

No arquivo crawler.py, na função main(), você pode mudar:

   crawler.crawlar('http://localhost:80/', max_paginas=50)

- O primeiro parâmetro é a URL inicial
- max_paginas é o limite de páginas que o crawler vai visitar
- verbose=False deixa a execução silenciosa (sem print no terminal)

Exemplo pra testar no site do CERN:

   crawler.crawlar('http://info.cern.ch/hypertext/WWW/TheProject.html', 
                   max_paginas=30)

================================================================================
O QUE APARECE NO TERMINAL
================================================================================

[1] Visitando: http://localhost/
  ↳ 5 links encontrados
  ↳ Fila: 5 | Visitados: 1

[2] Visitando: http://localhost/page1.html
  ↳ 3 links encontrados
  ↳ Fila: 7 | Visitados: 2

...

Crawler finalizado! Visitados: 28
Relatório salvo em: relatorio_crawler.txt

================================================================================
ESTRUTURA DOS ARQUIVOS
================================================================================

O projeto tem só esses arquivos:

crawler.py              # O código
relatorio_crawler.txt   # O relatório que o programa gera
README.txt              # Esse txt para explicação rápida do projeto

================================================================================
SE DER ERRO
================================================================================

"ModuleNotFoundError: No module named 'bs4'"
-> Esqueceu de instalar o BeautifulSoup: pip3 install beautifulsoup4

"Connection refused" ou "Timeout"
-> O servidor Docker não tá rodando. Verifica se o container está ativo.

"Address already in use" no Docker
-> Porta ocupada. Usa docker run -p 8080:80 no lugar.

"Permission denied" no Linux (meu caso)
-> Precisa de sudo: sudo docker run -p 80:80 robertovrf/...

================================================================================
OBSERVAÇÕES
================================================================================

- O código usa sockets, não usei requests nem nada do tipo
- As requisições HTTP são montadas na mão (com f-string)
- O BeautifulSoup só serve pra extrair os links do HTML, não faz requisição
- O crawler guarda URLs já visitadas num set() pra não ficar repetindo página
- Redirecionamentos 301 e 302 são seguidos automaticamente
- Timeout de 10 segundos pra cada página

================================================================================
FIM
================================================================================
