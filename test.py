import requests
# r = requests.get('https://events.shanghai.nyu.edu/live/widget/5')
r = requests.get('https://events.shanghai.nyu.edu/live/fuck')
if r.status_code == 404:
    print('http 404')
else:
    print(r.content)
#print(r.status_code)
