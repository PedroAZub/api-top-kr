from flask import Flask, Response
import cloudscraper
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Essa rota captura qualquer coisa que vier na URL
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = "https://www.leagueofgraphs.com/summoner/kr/FURIA+Ayu-1103"
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        
        if "Just a moment" in response.text:
            return Response("Bot bloqueado (Cloudflare).", mimetype='text/plain')

        soup = BeautifulSoup(response.text, 'html.parser')

        # Busca a caixa de rank
        rank_div = soup.find("div", class_="league-rank")
        
        if rank_div:
            texto_completo = rank_div.get_text().strip()
            # O texto vem assim: "Rank: 345 (KR: 95)"
            # O Regex abaixo ignora o 345 e pega só o 95 dentro do parenteses
            match = re.search(r'\(KR:\s*([\d,]+)\)', texto_completo)
            
            if match:
                rank_kr = match.group(1)
                return Response(f"FURIA Ayu: Rank #{rank_kr} (KR)", mimetype='text/plain')
            
            # Se não achar o KR, tenta limpar o texto e mandar o que achou
            return Response(f"FURIA Ayu: {texto_completo}", mimetype='text/plain')
            
        # Fallback (caso ele caia pra GM ou Mestre)
        tier = soup.find("div", class_="league-tier-name")
        lp = soup.find("div", class_="league-points")
        if tier and lp:
            return Response(f"FURIA Ayu: {tier.get_text().strip()} - {lp.get_text().strip()}", mimetype='text/plain')

        return Response("Rank não encontrado.", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro: {str(e)}", mimetype='text/plain')