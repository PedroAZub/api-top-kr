from flask import Flask, Response
import cloudscraper
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = "https://www.leagueofgraphs.com/summoner/kr/FURIA+Ayu-1103"
    
    # Tenta usar um navegador Desktop Windows para enganar melhor
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    
    try:
        response = scraper.get(url)
        
        # Cria o objeto soup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- ESTRATÉGIA DE FORÇA BRUTA ---
        # Pega TODO o texto da página, ignorando HTML tags
        texto_pagina = soup.get_text()
        
        # Procura pelo padrão "(KR: numero)" em qualquer lugar do texto
        match = re.search(r'\(KR:\s*([\d,]+)\)', texto_pagina)
        
        if match:
            rank_kr = match.group(1)
            return Response(f"FURIA Ayu: Rank #{rank_kr} (KR)", mimetype='text/plain')
            
        # --- SE FALHAR, DEBUGAR ---
        # Vamos descobrir o que o bot está vendo
        titulo_pagina = soup.title.string if soup.title else "Sem Título"
        
        # Checa se achou pelo menos o elo (Challenger/Grandmaster)
        if "Challenger" in texto_pagina:
             return Response(f"Achei 'Challenger' no texto, mas não o número do rank (KR). Título: {titulo_pagina}", mimetype='text/plain')
             
        # Se não achou nada, devolve o título da página para sabermos se foi bloqueio
        return Response(f"Erro: Rank não achado. O site carregou com o título: '{titulo_pagina}'", mimetype='text/plain')

    except Exception as e:
        return Response(f"Erro interno: {str(e)}", mimetype='text/plain')