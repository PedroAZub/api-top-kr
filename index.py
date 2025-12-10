from flask import Flask, Response
import cloudscraper
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Força a URL em inglês (/en/) para garantir o padrão de texto
    url = "https://www.leagueofgraphs.com/en/summoner/kr/FURIA+Ayu-1103"
    
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    # Headers para forçar inglês e desktop
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
            # Ex: (KR: 95) ou (KR: #95)
            match = re.search(r'KR:?\s*#?([\d,]+)', texto, re.IGNORECASE)
            
            if match:
                rank_kr = match.group(1)
                return Response(f"O Rank do Ayu na KR é: #{rank_kr}", mimetype='text/plain')
            
            # Se não achou KR, vê se tem apenas o Rank Global
            # Ex: Rank: 345
            match_global = re.search(r'Rank:?\s*#?([\d,]+)', texto, re.IGNORECASE)
            if match_global:
                 return Response(f"Rank Global: #{match_global.group(1)} (Regional não aparece)", mimetype='text/plain')

        # Se não achou a div, tenta varrer o texto bruto da página
        full_text = soup.get_text()
        match_brute = re.search(r'\(KR:?\s*#?([\d,]+)\)', full_text)
        if match_brute:
            return Response(f"O Rank do Ayu na KR é: #{match_brute.group(1)}", mimetype='text/plain')

        return Response("Rank KR não encontrado na página (Pode ter caído do Top Ladder).", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro: {str(e)}", mimetype='text/plain')