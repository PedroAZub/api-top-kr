from flask import Flask
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online! Use /rank para ver o elo."

@app.route('/rank')
def get_rank_scraping():
    # URL do perfil do Ayu (pode mudar se ele trocar de nick)
    url = "https://www.leagueofgraphs.com/summoner/kr/FURIA+Ayu-1103"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: return "Erro ao acessar site."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tenta achar a posição exata (Ladder Rank)
        rank_div = soup.find("div", class_="league-rank")
        if rank_div:
            return f"FURIA Ayu (KR): {rank_div.get_text().strip()}"
            
        # Fallback para Elo + PDL
        tier_div = soup.find("div", class_="league-tier-name")
        lp_div = soup.find("div", class_="league-points")
        if tier_div and lp_div:
            return f"FURIA Ayu (KR): {tier_div.get_text().strip()} - {lp_div.get_text().strip()}"
            
        return "Rank não encontrado (Unranked?)"
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == '__main__':
    # Isso é só para testar no seu PC se quiser
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)