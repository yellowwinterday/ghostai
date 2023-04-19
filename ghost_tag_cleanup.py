import os
import sys
import re
import json
import requests # pip install requests
import jwt	# pip install pyjwt
import configparser
import pandas as pd
import numpy as np
import logging

from datetime import datetime as date


config = configparser.ConfigParser()
config.read('./.env')
key = ""

try:
    key = config['BASIC']['GHOST_ADMIN_API_KEY']
except KeyError as e:
    print("Not finding key in config. Try environment.")

if len(key) == 0:
    if 'GHOST_ADMIN_API_KEY' not in os.environ:
        print("Missing GHOST_ADMIN_API_KEY. Please set the GHOST_ADMIN_API_KEY environment variable before running the script. You can find it by following instructions here: https://ghost.org/docs/admin-api/")
        exit(0)
    else:
        key = os.environ.get('GHOST_ADMIN_API_KEY')

print("GHOST_ADMIN_API_KEY ready")


url = config['BASIC']['GHOST_SITE_URL']
log_path = config['BASIC']['LOG_PATH']
output_path = config['BASIC']['EMBEDDING_OUTPUT_PATH']
max_related_count = int(config['BASIC']['MAX_RELATED_BLOG_COUNT'])

if not os.path.exists(output_path):
    os.makedirs(output_path)
    print("Directory "+str(output_path)+" created.")
#else:
#    print("Directory "+str(output_path)+" already exists.")

if not os.path.exists(log_path):
    os.makedirs(log_path)
    print("Directory "+str(log_path)+" created.")
#else:
#    print("Directory "+str(log_path)+" already exists.")

# Configure logging
logging.basicConfig(
    filename=str(log_path)+'/tagging.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

clean_internal = False
clean_public = False
if len(sys.argv) > 1:
    if str(sys.argv[1]).upper() == "BOTH":
        print('Clean up both public and internal tags')
        logging.info('Clean up both public and internal tags')
        clean_internal = True
        clean_public = True
    elif str(sys.argv[1]).upper() == "INTERNAL":
        clean_internal = True
        print('Clean up internal tags')
        logging.info('Clean up internal tags')
    elif str(sys.argv[1]).upper() == "PUBLIC":
        clean_public = True
        print('Clean up public tags')
        logging.info('Clean up public tags')

if not clean_public and not clean_internal:
    print('Please choose at least one clean up type: both / internal / public')
    sys.exit()

def fetchBlogPage(page):
    # Split the key into ID and SECRET
    id, secret = key.split(':')

    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }

    # Create the token (including decoding secret)
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

    # Make an authenticated request to list all posts
    headers = {'Authorization': 'Ghost {}'.format(token)}
    geturl = url+'ghost/api/admin/posts/?page='+str(page)

    return requests.get(geturl, headers=headers)


def ghost_cleanup_tags(site_url,blog_id):

    # Split the key into ID and SECRET
    id, secret = key.split(':')

    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }

    # Create the token (including decoding secret)
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

    # Make an authenticated request to create a post
    geturl = site_url+'ghost/api/admin/posts/'+blog_id
    headers = {'Authorization': 'Ghost {}'.format(token)}

    try:
        r = requests.get(geturl, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)

    #print(r.json()['posts'][0]['updated_at'])
    updated_at = r.json()['posts'][0]['updated_at']
    original_tags =r.json()['posts'][0]['tags']

    # Make an authenticated request to edit an item
    headers = {'Authorization': 'Ghost {}'.format(token)}
    editurl = site_url+'ghost/api/admin/posts/'+blog_id+'/?formats=mobiledoc%2Clexical'


    tag_dict_array = []

    if not clean_internal:
        for original_tag in original_tags:
            tag_dict = {'name':str(original_tag['name']),'slug':str(original_tag['slug'])}
            if original_tag['name'][0] == '#':
                tag_dict_array.append(tag_dict)

    if not clean_public:
        for original_tag in original_tags:
            tag_dict = {'name':str(original_tag['name']),'slug':str(original_tag['slug'])}
            if original_tag['name'][0] != '#':
                tag_dict_array.append(tag_dict)

    logging.info('Updated tags:'+str(tag_dict_array))

    body = {
        "posts":[
            {
                "tags":tag_dict_array,
                "updated_at":updated_at
            }
        ]
    }

    try:
        r = requests.put(editurl, json=body, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Update tag failed due to request: " + str(e))
        return False
    except Exception as e:
        print("Update tag failed: " + str(e))
        return False
    #print(r.json()['posts'][0]['tags'])
    return True

response = fetchBlogPage(1)

if int(response.status_code) != 200:
    sys.exit('Failed to load blog list, please check ./.env to make sure all keys are set.')

total_page = int(response.json()['meta']['pagination']['pages'])
total_blog = int(response.json()['meta']['pagination']['total'])
print(str(total_page)+' pages to load')
print(str(total_blog)+' blogs to load')

count = 0
for page in range(1,total_page+1):
    response = fetchBlogPage(page).json()
    posts = response['posts']
    for post in posts:
        id = post['id']
        ghost_cleanup_tags(url,id)
        tagging_file_path = output_path+"/blog-"+str(id)+"-tags.txt"
        if clean_public and os.path.exists(tagging_file_path):
            os.remove(tagging_file_path)
            logging.info("Also deleted existing tag file for blog-"+str(id)+".")
        print("Blog-"+str(id)+"cleaned up")


print("Total "+str(count)+" blog tag cleaned up.")
logging.info("Total "+str(count)+" blog tagged.")

