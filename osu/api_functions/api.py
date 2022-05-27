from tabnanny import check
from time import time
from ossapi import *
from dotenv import load_dotenv
import os
import datetime as dt
import requests
from dateutil import relativedelta as rdelta
from bs4 import BeautifulSoup
import json
load_dotenv()

client_secret = os.getenv('OSU_TOKEN')
client_id = os.getenv('OSU_CLIENT')
api = OssapiV2(client_id, client_secret)


####################


def mapper(username: str): #gives a list of mapping info about a user using ossapi.
    r = api.user(api.search(query=username).users.data[0].id)
    if r.username.lower() != username.lower():
        print("seems the username could not be found.")
        return 0

    id = r.id
    gravecount = r.graveyard_beatmapset_count
    followers = r.mapping_follower_count

    #find information about the newest map.
    try:
        temp1=api.user_beatmaps(user_id=id, type_="pending")[0]
    except:
        try:
            temp1=api.user_beatmaps(user_id=id, type_="graveyard")[0]
        except:
            temp1=None
    
    try:
        temp2 = api.user_beatmaps(user_id=id, type_="ranked")[0]
    except:
        temp2=None
    
    if temp1==None:
        if temp2==None:
            print("user has no uploaded maps.")
            return 0

        new = temp2
    elif temp1.submitted_date > temp2.submitted_date:
        new = temp1
    else:
        new = temp2

    new_info = [new.artist+ ' - ' + new.title, new.beatmaps[0].url, new.beatmaps[0].last_updated.date(), new.covers.card]
            
    #try find oldest graved, else ranked, else pending map; else set the oldest date to 0.
    try:
        x= dt.datetime.replace(api.user_beatmaps(user_id=id, type_="graveyard", offset=gravecount-1)[0].submitted_date, tzinfo=None)
        valid = 1
    
    except:
        try:
            x= dt.datetime.replace(api.user_beatmaps(user_id=id, type_="ranked", offset=r.ranked_and_approved_beatmapset_count-1)[0].submitted_date, tzinfo=None)
            valid = 1
        except:
            try:
                x= dt.datetime.replace(api.user_beatmaps(user_id=id, type_="pending", offset=r.pending_beatmapset_count-1)[0].submitted_date, tzinfo=None)
                valid = 1
            except:
                day = month = year = 0
            
    if valid==1:
        rd = rdelta.relativedelta(dt.date.today(),x.date())
        day = rd.days
        month = rd.months
        year = rd.years

    info = {
        "username": r.username,
        "id": id,
        "mapsets_rpgl": [r.ranked_and_approved_beatmapset_count, r.pending_beatmapset_count, r.graveyard_beatmapset_count, r.loved_beatmapset_count],
        "oldest_ymd": [year, month, day],
        "followers": followers,
        "avatar_url": r.avatar_url,
        "newest": new_info
    }
    return info



def bn_info(option: int): #gives info about open osu BNs using mappersguild API; option 0 returns dictionary with separated statuses, else it returns 1 overall list with the status appended to each BN.
    response = requests.get("https://bn.mappersguild.com/relevantInfo").content
    bn_info = json.loads(response.decode('utf-8'))['allUsersByMode']
    for x in range(len(bn_info)):
        if bn_info[x]["_id"] == "osu": #if u need another mode or want to change to all modes, just rewrite this Lol
            break
        x+=1
    
    overall=[]
    closed=[]
    unknown=[]
    open=[]
    for i in range(len(bn_info[x]['users'])):
        if "requestStatus" in bn_info[x]['users'][i]:
            if "closed" in bn_info[x]['users'][i]['requestStatus']:
                if option==0:
                    closed.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId']])
                else:
                    overall.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId'], 'closed'])

            elif bn_info[x]['users'][i]['requestStatus'] == []:
                if option==0:
                    unknown.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId']])
                else:
                    overall.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId'], 'unknown'])

            else:
                if option==0:
                    open.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId']])
                else:
                    overall.append([bn_info[x]['users'][i]['username'], bn_info[x]['users'][i]['osuId'], 'open'])

        i+=1

    if option==0:  
        info = {
        'open':open,
        'closed':closed,
        'unknown':unknown
        }
        return info
    else:
        return overall



def forum_queue_info():
    changes_dict = {}
    r = requests.get("https://osu.ppy.sh/community/forums/60")
    soup = BeautifulSoup(r.content, 'html.parser')
    forum = soup.select('.forum-list__items')[2] #selects forum posts in the html
    latest_posts = forum.find_all('li', attrs={'class':'forum-topic-entry clickable-row js-forum-topic-entry t-forum-category-beatmaps'})[:10] #gets first 10 (since we're checking regularly, we don't need all 30 of them)
    for post in latest_posts:
        user_colour = post.find_all('span', attrs={'class': 'forum-topic-entry__user-icon'})[0].get("style") #non-users have colour
        if 'background-color' in user_colour:
            forum_id = post.get("data-topic-id")
            forum_object = api.forum_topic(forum_id, sort='id_desc')
            time_between_posts = forum_object.posts[0].created_at - forum_object.posts[1].created_at
            user_title = api.user(forum_object.posts[0].user_id).title

            if time_between_posts > dt.timedelta(days=2): #only return if it has been 2 days since the last post.
                if user_title is None:
                    changes_dict[forum_id] = [str(forum_object.topic.title),  time_between_posts, f"**{api.user(forum_object.posts[0].user_id).username}**: "+BeautifulSoup(forum_object.posts[0].body.html,features='lxml').get_text('\n').split('\n',1)[0]+"..."]
                else:
                    changes_dict[forum_id] = [str(forum_object.topic.title),  time_between_posts, f"**{api.user(forum_object.posts[0].user_id).username}** ***({user_title})***: "+BeautifulSoup(forum_object.posts[0].body.html,features='lxml').get_text('\n').split('\n',1)[0]+"..."]
            
    if changes_dict: return changes_dict
    return None

def gform_info(urls: list):
    forms_dict = {}
    for url in urls:
        user_agent = {'Referer':url+'/viewform','User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
        r = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(r.content, 'html.parser')
        #
        divs = soup.find_all('div')
        i=0
        for div in divs:
            if div.has_attr('role'):
                if div['role'] == 'heading':
                    break
            i+=1
        title_header = f"{' '.join((divs[i+1].text.split(' '))[:10])}..." #only returning the header instead of title, but title will be in div[i] (if i need it)
        inputs = len(soup.find_all("input"))
        forms_dict[url] = {'title': title_header, 
                            'inputs':inputs}

    return forms_dict #returns dict like {gform: ['title of gform: header of gform', no. of inputs in form]}


