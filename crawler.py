import socket
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime

class WebCrawler:
    def __init__(self):
        self.visitados = set()
        self.fila = []
        self.relatorio = []
    
    def parse_url(self, url):
        """Extrai host, porta e caminho da URL"""
        parsed = urlparse(url)
        
        host = parsed.hostname or 'localhost'
        porta = parsed.port or 80
        caminho = parsed.path or '/'
        
        if parsed.query:
            caminho += '?' + parsed.query

        return host, porta, caminho
    
    def construir_requisicao(self, host, caminho):
        """Requisição HTTP manualmente"""
        request = f"GET {caminho} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "User-Agent: MeuCrawler/1.0\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"
        return request.encode('utf-8')
    
    def fazer_requisicao_http(self, url):
        """Requisição HTTP usando sockets"""
        try:
            host, porta, caminho = self.parse_url(url)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, porta))
            
            requisicao = self.construir_requisicao(host, caminho)
            sock.send(requisicao)
            
            resposta_bytes = b''
            while True:
                dados = sock.recv(4096)
                if not dados:
                    break
                resposta_bytes += dados
            
            sock.close()
            return self.interpretar_resposta(resposta_bytes)
        
        except socket.timeout:
            return {'codigo': 'ERRO', 'descricao': 'Timeout', 'corpo': '', 'cabecalhos': {}}
        except Exception as e:
            return {'codigo': 'ERRO', 'descricao': f'Erro: {str(e)}', 'corpo': '', 'cabecalhos': {}}
    
    def interpretar_resposta(self, dados_bytes):
        """Interpreta resposta HTTP"""
        descricoes = {
            '200': 'OK - Requisição bem sucedida',
            '301': 'Moved Permanently - Redirecionamento permanente',
            '302': 'Found - Redirecionamento temporário',
            '404': 'Not Found - Página não encontrada',
            '500': 'Internal Server Error - Erro interno do servidor'
        }
        
        try:
            #Decodifica a resposta
            try:
                dados = dados_bytes.decode('utf-8')
            except:
                dados = dados_bytes.decode('latin-1')
            
            #Separa os cabeçalhos do corpo
            if '\r\n\r\n' in dados:
                cabecalho_str, corpo = dados.split('\r\n\r\n', 1)
            else:
                cabecalho_str = dados
                corpo = ''
            
            #Extrai o status code
            linhas = cabecalho_str.split('\n')
            primeira_linha = linhas[0].strip()
            partes = primeira_linha.split(' ', 2)
            codigo = partes[1] if len(partes) >= 2 else 'ERRO'
            mensagem = partes[2] if len(partes) > 2 else ''
            
            #Extrai cabeçalhos
            cabecalhos = {}
            for linha in linhas[1:]:
                if ': ' in linha:
                    chave, valor = linha.split(': ', 1)
                    cabecalhos[chave.lower()] = valor
            
            resultado = {
                'codigo': codigo,
                'descricao': descricoes.get(codigo, mensagem),
                'corpo': corpo,
                'cabecalhos': cabecalhos
            }
            
            if codigo in ['301', '302'] and 'location' in cabecalhos:
                resultado['redirect'] = cabecalhos['location']
            
            return resultado
        
        except Exception as e:
            return {'codigo': 'ERRO', 'descricao': f'Erro: {str(e)}', 'corpo': '', 'cabecalhos': {}}
    
    def extrair_links(self, html, url_atual):
        """Extrai links do HTML usando BeautifulSoup"""
        links = []
        if not html:
            return links
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag_a in soup.find_all('a'):
                href = tag_a.get('href')
                if href and href.strip():
                    href = href.strip()
                    
                    #Ignora âncoras
                    if href.startswith('#'):
                        continue
                    
                    #emove âncoras do meio da URL
                    #    Mas preserva URLs que têm # como partedo caminho
                    if '#' in href:
                        # Separa a URL da ancora
                        href = href.split('#')[0]
                        # Se depois de remover a âncora ficou vazio, ignora
                        if not href:
                            continue
                    
                    #Converte URL relativa para absoluta
                    url_completa = urljoin(url_atual, href)
                    
                    #Filtra apenas URLs HTTP
                    if url_completa.startswith('http://'):
                        parsed = urlparse(url_completa)
                        #Limitando os hosts permitidos
                        if parsed.hostname in ['localhost', '127.0.0.1', 'info.cern.ch']:
                            links.append(url_completa)
            
            # Remove duplicata
            links = list(dict.fromkeys(links))
            
        except Exception as e:
            print(f"Erro ao extrair links: {e}")
        
        return links
    
    def crawlar(self, url_inicial, max_paginas, verbose=True):
        """Executa o crawler"""
        self.fila.append(url_inicial)
        
        print(f"Iniciando crawler: {url_inicial}")
        print(f"Limite: {max_paginas} páginas\n")
        
        while self.fila and len(self.visitados) < max_paginas:
            url_atual = self.fila.pop(0)
            
            if url_atual in self.visitados:
                continue
            
            if verbose:
                print(f"[{len(self.visitados) + 1}] Visitando: {url_atual}")
            
            resposta = self.fazer_requisicao_http(url_atual)
            
            self.relatorio.append({
                'url': url_atual,
                'codigo': resposta.get('codigo', 'ERRO'),
                'descricao': resposta.get('descricao', 'Falha')
            })
            
            self.visitados.add(url_atual)
            
            #Trata os redirecionamento
            if resposta.get('codigo') in ['301', '302'] and 'redirect' in resposta:
                nova_url = resposta['redirect']
                if not nova_url.startswith('http'):
                    nova_url = urljoin(url_atual, nova_url)
                
                if nova_url not in self.visitados and nova_url not in self.fila:
                    self.fila.append(nova_url)
                if verbose:
                    print(f"  ↳ Redireciona para: {nova_url}")
            
            # Extrai links de páginas 200 ok
            elif resposta.get('codigo') == '200':
                links = self.extrair_links(resposta.get('corpo', ''), url_atual)
                for link in links:
                    if link not in self.visitados and link not in self.fila:
                        self.fila.append(link)
                if verbose and links:
                    print(f"  ↳ {len(links)} links encontrados")
            
            if verbose:
                print(f"  ↳ Fila: {len(self.fila)} | Visitados: {len(self.visitados)}\n")
        
        print(f"Crawler finalizado! Visitados: {len(self.visitados)}")
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """Gera relatório em arquivo"""
        with open('relatorio_crawler.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DO WEB CRAWLER\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de páginas: {len(self.relatorio)}\n\n")
            
            # Estatísticas
            stats = {}
            for item in self.relatorio:
                stats[item['codigo']] = stats.get(item['codigo'], 0) + 1
            
            f.write("ESTATÍSTICAS:\n")
            f.write("-" * 40 + "\n")
            for codigo, count in sorted(stats.items()):
                f.write(f"  {codigo}: {count} página(s)\n")
            
            f.write("\nDETALHES:\n")
            f.write("-" * 40 + "\n")
            for i, item in enumerate(self.relatorio, 1):
                f.write(f"\n[{i}] {item['url']}\n")
                f.write(f"    Status: {item['codigo']} - {item['descricao']}\n")
        
        print(f"\nRelatório salvo em: relatorio_crawler.txt")

def main():
    print("CRAWLER - TESTE COM DOCKER")
    print("=" * 80)
    crawler = WebCrawler()
    crawler.crawlar('http://info.cern.ch/hypertext/WWW/TheProject.html', max_paginas=35)
    #para testar no servidor do docker só trocar a url acima e rodar o server no docker, tudo está explicado no README

if __name__ == "__main__":
    main()