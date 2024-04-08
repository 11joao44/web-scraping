# Imports do Python padrão
import csv
from time import sleep, time
from random import uniform

# Bibliotecas de terceiros
from concurrent.futures import ThreadPoolExecutor
from googletrans import Translator
from bs4 import BeautifulSoup
from requests import get
import pandas as pd

# Simulando um Navegador no Sistema Windows
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}

def navegar_site(url):
    return BeautifulSoup(get(url, headers=headers).content, 'html.parser')

def extracao_series_detalhes(serie_url):
    sleep(uniform(0, 0.2))
    pagina_serie = navegar_site(serie_url)
    detalhes_serie = pagina_serie.find('div',attrs={'sc-4e4cc5f9-3 dDRspk'})
 
    if pagina_serie.find('title').text == '404 Error - IMDb':
        print('404 Error - IMDb A URL solicitada não foi encontrada no servidor.')
    else:
        titulo = detalhes_serie.find('span', attrs='hero__primary-text').text
        ano = detalhes_serie.find('a', attrs={'class':'ipc-link ipc-link--baseAlt ipc-link--inherit-color'}).text
        avaliacao = detalhes_serie.find('div', attrs={'data-testid':'hero-rating-bar__aggregate-rating__score'}).text
        trama = Translator().translate(pagina_serie.find('span',attrs={'data-testid':'plot-xl'}).text, dest='pt').text

    with open('series.csv', mode='a') as file:
            movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if all([titulo, ano, avaliacao, trama]):
                movie_writer.writerow([titulo, ano, avaliacao, trama])
 
# IMDB Extraindo as Séries mais populares - 100 Séries
def extracao_series(soup, max_threads):
    list_series = soup.find('div', attrs={'data-testid':'chart-layout-main-column'}).find('ul')
    all_series = list_series.find_all('li')
    series_url = [f'https://imdb.com{movie.find('a')['href']}' for movie in all_series] # Capturando todas as urls das 100 Séries
    
    with ThreadPoolExecutor(max_workers=min(max_threads, len(series_url))) as executor:
        executor.map(extracao_series_detalhes,series_url)

def main():
    start_time = time()
    site = navegar_site('https://www.imdb.com/chart/tvmeter/?ref_=nv_tvv_mptv')
    extracao_series(site, max_threads=10)
    end_time = time()
    print(f'Total time taken: {int((end_time-start_time)//60)} minutos e {int((end_time-start_time)%60)} segundos')
    
if __name__ == '__main__':
    main()