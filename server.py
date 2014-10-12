from flask import *
import re, urllib, urllib2, json, HTMLParser, sys

app = Flask(__name__)

listings_to_retrieve = 100
picture_limit = 100
api_url = 'http://www.reddit.com/top.json?sort=top'+ '&limit=' + str(listings_to_retrieve) 
agent = 'Slideshow bot /u/aho338/'
safe="%/:=&?~#+!$,;'@()*[]"
clean_only = True

try:
    if sys.argv[1] == 'clean':
        clean_only = True
    if sys.argv[1] == 'dirty':
        clean_only = False
except IndexError:
    pass
# print(post_data)


def fetch_listings(api_url_string, listing_count, agnt, clean_only = True):
    pic_list = []
    image_num = 0
    while len(pic_list) < picture_limit:
        req = urllib2.Request(api_url_string)
        req.add_header('User-Agent', agnt)
        # print(req.header_items())
        try:
            response = urllib2.urlopen(req)
        except (urllib2.HTTPError,urllib2.URLError):
            return []
        post_data = json.loads(response.read()) # store post data
        data_shortcut = post_data['data']['children']
        try:
            for listing_number in range(listing_count):
                if len(pic_list) >= picture_limit:
                    break
                listing_url = data_shortcut[listing_number]['data']['url']
                domain = data_shortcut[listing_number]['data']['domain']
                if is_picture(listing_url, domain):
                    image_info={}
                    image_info['title']=HTMLParser.HTMLParser().unescape(data_shortcut[listing_number]['data']['title'])

                    if is_gifv(listing_url):
                        #url ends in .gifv: return .gif
                        image_info['url']=listing_url[0:-1]
                    elif has_img_url(listing_url):
                        #url ends in .jpg/.png/.gif
                        image_info['url']=listing_url
                    else:
                        #domain == imgur.com
                        #hacky way to grab imgur images without using their API
                        image_info['url']=convert_to_img_url(listing_url)
                        
                    image_info['id']='image-'+str(image_num)

                    image_info['subreddit'] = data_shortcut[listing_number]['data']['subreddit']
                    image_info['permalink'] = 'http://www.reddit.com'+data_shortcut[listing_number]['data']['permalink']
                    if clean_only and data_shortcut[listing_number]['data']['over_18']:
                        # image_num = image_num + 1
                        continue
                    else:
                        pic_list.append(image_info)
                        image_num = image_num + 1
        except IndexError:
            break
        if(post_data['data']['after']):
            api_url_string = api_url_string+'&after='+post_data['data']['after']
    return pic_list

def is_gifv(url):
    if re.search(r'\.gifv',url):
        return True
    return False

def is_album(url):
    return (url.find("imgur.com/a/") != -1) or (url.find("imgur.com/gallery/") != -1)

def has_img_url(url):
    if re.search(r'\.jpg|\.png|\.gif',url):
        return True
    return False

def is_picture(url, domain):
    return not is_album(url) and (has_img_url(url) or domain == "imgur.com")

def convert_to_img_url(url):
    position = url.find("//")+2
    # check for album
    if url[len(url)-1] == '/':
        return url[:position] + "i." + url[position:-1] + ".gif"
    else:
        return url[:position] + "i." + url[position:] + ".gif"
    
@app.route("/")
@app.route("/<time>/")
@app.route("/r/<sub>/")
@app.route("/r/<sub>/<time>/")
def index(sub='', time='day'):
    # purge inputs
    sub = urllib.quote(sub, safe)
    time = urllib.quote(time, safe)

    if sub:
        api_url = 'http://www.reddit.com/r/'+sub+'/top.json?sort=top'+ '&t='+time+ '&limit=' + str(listings_to_retrieve)
    else:
        api_url = 'http://www.reddit.com/top.json?sort=top'+ '&t='+time+ '&limit=' + str(listings_to_retrieve)
    
    if time == 'week':
        time_title = 'This Week'
    elif time == 'month':
        time_title = 'This Month'
    elif time == 'year':
        time_title = 'This Year'
    elif time == 'all':
        time_title = 'of All Time'
    else:
        time_title = 'Today'
    list_of_pics = fetch_listings(api_url,listings_to_retrieve, agent, clean_only)

    subreddit_name = None
    if sub == 'all':
        subreddit_name = '/r/all'
    if sub and list_of_pics != [] and sub != 'all': 
        subreddit_name = '/r/'+list_of_pics[0]['subreddit'].title()

    return render_template('index.html', pics = list_of_pics, image_count = len(list_of_pics), subreddit_name = subreddit_name, time_title = time_title)

@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, this page cannot be found!'

if __name__ == "__main__":
    app.run(debug=False)
    app.run()