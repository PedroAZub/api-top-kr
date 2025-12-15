from flask import Flask, Response, request
import cloudscraper
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # 1. Pega os dados da URL
    # Se não informar nada, busca o Ayu como padrão
    nick = request.args.get('nick', 'FURIA Ayu')
    tag = request.args.get('tag', '1103')
    
    # Prepara o nick para o link (substitui espaço por +)
    nick_url = nick.replace(' ', '+')
    
    # Monta a URL dinâmica
    url = f"https://www.leagueofgraphs.com/en/summoner/kr/{nick_url}-{tag}"
    
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = scraper.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura especificamente a div de rank
        rank_div = soup.find("div", class_="league-rank")
        
        if rank_div:
            texto = rank_div.get_text()
            
            # Tenta pegar o que está entre parenteses e tem KR
            match = re.search(r'KR:?\s*#?([\d,]+)', texto, re.IGNORECASE)
            
            if match:
                rank_kr = match.group(1)
                # Mantendo a sua mensagem original, adaptando apenas o nome
                return Response(f"O Rank do {nick} na KR é: #{rank_kr}", mimetype='text/plain')
            
            # Se não achou KR, vê se tem apenas o Rank Global
            match_global = re.search(r'Rank:?\s*#?([\d,]+)', texto, re.IGNORECASE)
            if match_global:
                 return Response(f"Rank Global: #{match_global.group(1)} (Regional não aparece)", mimetype='text/plain')

        # Se não achou a div, tenta varrer o texto bruto da página
        full_text = soup.get_text()
        match_brute = re.search(r'\(KR:?\s*#?([\d,]+)\)', full_text)
        if match_brute:
            return Response(f"O Rank do {nick} na KR é: #{match_brute.group(1)}", mimetype='text/plain')

        return Response(f"Rank KR de {nick} não encontrado na página.", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro: {str(e)}", mimetype='text/plain')