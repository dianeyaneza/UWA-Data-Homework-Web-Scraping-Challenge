from bs4 import BeautifulSoup
from splinter import Browser
import pymongo
import requests

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=True)

def scrape():
    browser = init_browser()

    ## Scrape the NASA Mars News Site 
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    slide_element = news_soup.select_one("ul.item_list li.slide")
    # collect the latest News Title. 
    mars_news_title = slide_element.find('div', class_='content_title').text
    # collect the Paragraph Text.
    mars_news_paragraph = slide_element.find('div', class_='article_teaser_body').text


    ## Scrape the Featured Mars Image 
    image_url ='https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(image_url)
    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')
    # Make sure to find the image url to the full size .jpg image.
    feat_img = image_soup.find('img', class_='headerimage').get('src')
    # Make sure to save a complete url string for this image.
    feat_image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{feat_img}'


    ## Visit the Mars Facts webpage and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    mars_facts_url = "https://space-facts.com/mars/"
    table = pd.read_html(mars_facts_url)
    table[0]
    # Use Pandas to convert the data 
    marsfacts_df = table[0]
    marsfacts_df.columns = ["Facts", "Value"]
    marsfacts_df.set_index(["Facts"])
    # Use Pandas to convert the data to a HTML table string.
    marsfacts_html = marsfacts_df.to_html()
    marsfacts_html = marsfacts_html.replace("\n","")
    marsfacts_df.to_html('marsfacts_table.html')


    ## Visit the USGS Astrogeology site to obtain high resolution images for each of Mars' hemispheres.
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
        img_dict = {'title': title.split('Enhanced')[0], 
                    'img_url': img_url}
        # Append the dictionary with the image url string and the hemisphere title to a list. This list will contain one dictionary for each hemisphere.
        hemis_img_urls.append(img_dict)

    ## Store the data into a dictionary
    mars_data = {
        "news_title": mars_news_title,
        "news_paragraph": mars_news_paragraph,
        "featured_image": feat_image_url,
        "mars_facts": marsfacts_html,
        "hemispheres": hemis_img_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data