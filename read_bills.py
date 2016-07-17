import json
import requests
import os

LOGIN_URL = 'https://online.leumi-card.co.il/Anonymous/Login/CardHoldersLogin.aspx'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'
COOKIE = 'checkcookie=yes; LBONLINE40=1; _dc_gtm_UA-37498201-17=1; NotAuthOnline40=md1yvk4sjzge5qqun4makgqi; CH40Request=d5a31ee2-337d-45e9-a379-eb389c342e8e; ct2=t=77821566-07e9-4a69-b01d-da09b538e22a; _ga=GA1.3.1570175447.1446665076'
#POST
def read_month():
    with open('pass.txt', 'r') as f:
        password = f.read()
    form_data = { \
      'ctl00$PlaceHolderMain$CardHoldersLogin1$txtUserName': 'odedbadt',
      'ctl00$PlaceHolderMain$CardHoldersLogin1$txtPassword': password}
    s = requests.Session()
    s.post(LOGIN_URL, data=form_data)
    import pdb
    pdb.set_trace()
    resp = s.get('https://online.leumi-card.co.il/Registred/HomePage.aspx')
    with open('resp.html', 'w') as f:
        f.write(resp.content)



if __name__ == '__main__':
  read_month()
