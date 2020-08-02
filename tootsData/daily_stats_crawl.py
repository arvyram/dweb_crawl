import requests
import json, time


headers = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    # 'Host': 'neibrconnect.com' , # This is another valid field
    'Content-Type': 'application/x-www-form/urlencoded',
    'Connection': 'Keep-Alive',
    'Referer': 'https://instances.social/list',
    'If-None-Match': 'W/"13d37c-SrZNFsmv+We9W5hd2P1dfT3EFRQ"'
}


url = 'https://instances.social/list.json?q%5Busers%5D=&strict=false' 


DATSET_FOLDER = 'daily_stats/'
# s1 = 1
# l1 = 21285838

# s2 =
# l2 = 98935898858839057


limit=30

resp = requests.get(url, headers=headers)

with open(DATSET_FOLDER + str(time.time()) + '.json', 'w' ) as fp:
	json.dump(resp.json(), fp)
