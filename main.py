import requests
from atproto import Client, models,client_utils
from bs4 import BeautifulSoup
import pickle
import random

def svg_to_png(url):
    parts = url.split("/")
    parts.insert(parts.index("commons")+1,"thumb")
    filename=parts[-1]
    new_filename = f"{filename}/1024px-{filename}.png"
    parts[-1]=new_filename
    return"/".join(parts)

def send_xeet(flag,caption):
    client = Client()
    client.login('BSKY_HANDLE','BSKY_PASSWORD')
    
    if flag['url'].endswith('.svg'):
        new_url=svg_to_png(flag['url'])
        root_post_ref = models.create_strong_ref(
                        client.send_image(text='Flag of the day',
                        image=requests.get(new_url,stream=True).content,
                        image_alt=caption)
                         )
    else:
        root_post_ref = models.create_strong_ref(
                        client.send_image(text='Flag of the day',
                        image=requests.get(flag['url'],stream=True).content,
                        image_alt=caption)
                         )
    text_builder = client_utils.TextBuilder()
    text_builder.text(caption)
    text_builder.text(' ')
    text_builder.link('source',flag['descriptionurl'])
    client.send_post(
        text_builder,
        reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref,root=root_post_ref)
        )
    
def get_caption(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    return soup.find(class_="wbmi-caption-value",lang="en").get_text()

def data():
    page_title = "Flags_of_extinct_states"
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "images",
        "prop":"imageinfo",
        "iiprop":"url",
        "titles":page_title,
        "gimlimit":"max",
        "format":"json"
    }
    return requests.get(url, params=params).json()
    
def main() ->None:
    try:
        with open('page.pkl','rb') as f:
            page = pickle.load(f)
        with open('wiki_flags.pkl','rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        with open('wiki_flags.pkl','rb') as f:
            data = pickle.load(f)
            pages = list(data['query']['pages'].keys())
            random.shuffle(pages)
            page = iter(pages)
            with open('page.pkl','wb') as f:
                pickle.dump(page,f)

    flag = data['query']['pages'][next(page)]['imageinfo'][0]
    
    description = get_caption(flag['descriptionurl'])
    send_xeet(flag,description)
    
if __name__=='__main__':
    main()
