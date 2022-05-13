from ossapi import *
from dotenv import load_dotenv
import os
import datetime as dt
import requests
from dateutil import relativedelta as rdelta
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

    


