from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from my_app.models import Search
from requests.compat import quote_plus

import requests

CRAIGSLIST_BASE_URL = 'https://bangalore.craigslist.org/search/'
CRAIGSLIST_BASE_IMAGE_URL = 'https://images.craigslist.org/'

DEFAULT_IMAGE_URL = 'https://livingstonmachinery.com/wp-content/plugins/oem-showcase-inventory/assets/images/noimage-found.png'

# Create your views here.
def home(request):
    """
    Home page
    """

    return render(request, 'base.html')

def search(request):
    """
    Search
    """

    results = []
    search_term = None
    search_filter = None

    # Get search params
    search_term = request.POST.get('search_term')
    search_filter = request.POST.get('group1')

    # Add to DB
    search = Search.objects.create(search=search_term)
    search.save()

    # Scrape Craigslist
    URL = f'{CRAIGSLIST_BASE_URL}{search_filter}?query={quote_plus(search_term)}&sort=rel'
    print(URL)
    req = requests.post(URL)
    soup = BeautifulSoup(req.text, 'html.parser')

    posts = soup.find_all('li', {'class' : 'result-row'})

    for post in posts:

        title = post.find(class_='result-title').text
        url = post.a.get('href')

        if post.find(class_='result-price'):
            price = post.find(class_='result-price').text
        else:
            price = "NA"
        
        if post.find(class_='result-image').get('data-ids'):
            raw_img_url = post.find(class_='result-image').get('data-ids').split(',')[0]
            img_url = f'{CRAIGSLIST_BASE_IMAGE_URL}{raw_img_url[2:]}_300x300.jpg'
        else:
            img_url = DEFAULT_IMAGE_URL

        results.append(
            {
                'title' : title,
                'url' : url,
                'price' : price,
                'img_url' : img_url
            }
        )

    data = {
        'search_term' : search_term,
        'results' : results
    }
    return render(request, 'my_app/search.html', data)