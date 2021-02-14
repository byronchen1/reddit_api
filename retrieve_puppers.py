import os
import shutil
from datetime import datetime
import pandas as pd
import requests


# Setup Token
AppID = ''
SECRET = ''
USER = ''
PW = ''
api_url = 'https://oauth.reddit.com'
save_dir = r'C:/'

base_url = 'https://www.reddit.com/'
data = {'grant_type': 'password', 'username': USER, 'password': PW}
auth = requests.auth.HTTPBasicAuth(AppID, SECRET)
r = requests.post(base_url + 'api/v1/access_token',
                  data=data,
                  headers={'user-agent': 'BBB'},
                  auth=auth)
d = r.json()
token = 'bearer ' + d['access_token']
base_url = 'https://oauth.reddit.com'
headers = {'Authorization': token, 'User-Agent': 'BBB'}
response = requests.get(base_url + '/api/v1/me', headers=headers)


def df_from_response(resp):
    df = pd.DataFrame()  # initialize dataframe

    # loop through each post retrieved from GET request
    for post in resp.json()['data']['children']:
        # append relevant data to dataframe
        df = df.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            'link_flair_css_class': post['data']['link_flair_css_class'],
            'url': post['data']['url'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'id': post['data']['id'],
            'kind': post['kind']

        }, ignore_index=True)

    return df


def download_img(image_url, sub_name):
    filename = image_url.split("/")[-1]
    is_img = (filename.split(".")[-1].lower() == 'jpg') | (filename.split(".")[-1].lower() == 'png')
    if is_img:
        # Open the url image, set stream to True, this will return the stream content.
        req = requests.get(image_url, stream=True)
        directory = f'{save_dir}{sub_name}_{datetime.today().strftime("%Y%m%d")}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Check if the image was retrieved successfully
        if req.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            req.raw.decode_content = True
            # Open a local file with wb ( write binary ) permission.
            with open(f'{directory}/{filename}', 'wb') as f:
                shutil.copyfileobj(req.raw, f)



params = {'limit': '100'}
subreddit = 'rarepuppers'
main_df = pd.DataFrame()

for i in range(5):
    # make request
    res = requests.get(f"https://oauth.reddit.com/r/{subreddit}/new",
                       headers=headers,
                       params=params)

    # get dataframe from response
    new_df = df_from_response(res)
    # take the final row (oldest entry)
    row = new_df.iloc[len(new_df) - 1]
    # create fullname
    fullname = row['kind'] + '_' + row['id']
    # add/update fullname in params
    params['after'] = fullname

    # append new_df to data
    main_df = main_df.append(new_df, ignore_index=True)


for i in range(len(main_df)):
    download_img(image_url=main_df['url'][i], sub_name=subreddit)
