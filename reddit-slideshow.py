import re, urllib.request, json

listings_to_retrieve = 100
api_url = 'http://www.reddit.com/top.json?'+ 'limit=' + str(listings_to_retrieve) 
response = urllib.request.urlopen(api_url)
post_data = json.loads(response.read().decode("utf-8")) # store post data
pic_list = []
#print(post_data)

data_shortcut = post_data['data']['children']
for listing_number in range(listings_to_retrieve):
	listing_url = data_shortcut[listing_number]['data']['url']
	is_a_picture = re.search(r'\.jpg|\.png|\.gif',listing_url)
	if is_a_picture:
		pic_list.append(listing_url)
		#print(listing_url)
print(pic_list)

