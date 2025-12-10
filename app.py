from flask import Flask
import cloudscraper # Biblioteca nova para passar pela proteção
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online! Use /rank"

@app.route('/rank')
def get_rank_scraping():
    url = "https://www.leagueofgraphs.com/summoner/kr/FURIA+Ayu-1103"
    
    # O cloudscraper cria um navegador fake mais convincente
    scraper = cloudscraper.create_scraper() 
    
    try:
        response = scraper.get(url)
        
        # Debug: Se o titulo da pagina for 'Just a moment...', fomos bloqueados
        if "Just a moment" in response.text:
            return "O site bloqueou o bot (Cloudflare). Tente mais tarde."

        soup = BeautifulSoup(response.text, 'html.parser')

        # Tenta achar a posição exata (Ladder Rank)
        rank_div = soup.find("div", class_="league-rank")
        if rank_div:
            # Limpa o texto (remove quebras de linha e espaços extras)
            rank_limpo = " ".join(rank_div.get_text().split())
            return f"FURIA Ayu (KR): {rank_limpo}"
            
        # Fallback: Tenta achar o Elo e PDL
        tier_div = soup.find("div", class_="league-tier-name")
        lp_div = soup.find("div", class_="league-points")
        
        if tier_div and lp_div:
            tier = tier_div.get_text().strip()
            lp = lp_div.get_text().strip()
            return f"FURIA Ayu (KR): {tier} - {lp}"
            
        # Se chegou aqui, printa o titulo da pagina para entender o erro
        page_title = soup.find("title").get_text() if soup.find("title") else "Sem titulo"
        return f"Não achei o rank. O site retornou a página: '{page_title}'"

    except Exception as e:
        return f"Erro interno: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)