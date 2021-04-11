import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser
import pymongo
import requests
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

def scrape():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    mars_news_title, mars_news_paragraph = news(browser)
    
    results = {
        "title": mars_news_title,
        "paragraph": mars_news_paragraph,
        "featured": image(browser),
        "facts": facts(browser),
        "hemis": hemis(browser)
        }
    browser.quit()
    print(results)

    return results

def news(browser):
    # Scrape the NASA Mars News Site
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    news_results = news_soup.find[0]("div", class_='list_text')
    for result in news_results:
        mars_news_title = result.find('div',class_="content_title").text
        mars_news_paragraph = result.find('div',class_="article_teaser_body").text
    return mars_news_title, mars_news_paragraph

    # collect the latest News Title and Paragraph Text.
    # mars_news_title = news_soup.find_all('div',class_="content_title")[1].text
    # mars_news_paragraph = news_soup.find_all('div',class_="article_teaser_body")[0].text
    # # mars_news_title = mars_news_title.text
    # # mars_news_paragraph = mars_news_paragraph.text
    # print(mars_news_title)
    # print(mars_news_paragraph)
    # return mars_news_title, mars_news_paragraph

def image(browser):
    # Scrape the Featured Mars Image
    image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(image_url)
    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')
    # Make sure to find the image url to the full size .jpg image.
    feat_img = image_soup.find('img', class_='headerimage').get('src')
    # Make sure to save a complete url string for this image.
    feat_image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{feat_img}'
    return feat_image_url

def facts(browser):
    # Visit the Mars Facts webpage and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    mars_facts_url = "https://space-facts.com/mars/"
    table = pd.read_html(mars_facts_url)
    # Use Pandas to convert the data
    marsfacts_df = table[0]
    marsfacts_df.columns = ['Fact','Value']
    marsfacts_df.set_index('Fact', inplace=True)
    # Use Pandas to convert the data to a HTML table string.
    marsfacts_html = marsfacts_df.to_html(header=False)
    return marsfacts_html

def hemis(browser):
    # Visit the USGS Astrogeology site to obtain high resolution images for each of Mars' hemispheres.
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemi_base_url = "https://astrogeology.usgs.gov"
    browser.visit(hemi_url)
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    hemis_img_urls = []

    results = hemi_soup.find_all("div", class_='item')
    for result in results:
        title = result.find('h3').text
        img_page_url = hemi_base_url + result.find('a')['href']
        
        # You will need to click each of the links to the hemispheres in order to find the image url to the full resolution image.
        response = requests.get(img_page_url)
        img_soup = BeautifulSoup(response.text, 'html.parser')
        
        img_url = img_soup.find('ul').li.a['href']
        
        img_dict = {'title': title.split('Enhanced')[0], 'img_url': img_url}

        # Append the dictionary with the image url string and the hemisphere title to a list. This list will contain one dictionary for each hemisphere.
        hemis_img_urls.append(img_dict)
    return hemis_img_urls