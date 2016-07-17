import requests

url = "https://online.leumi-card.co.il/Registred/Transactions/ChargesDeals.aspx"

payload = ""
headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'origin': "https://online.leumi-card.co.il",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'referer': "https://online.leumi-card.co.il/Registred/Transactions/ChargesDeals.aspx",
    'accept-encoding': "gzip, deflate",
    'accept-language': "en-US,en;q=0.8,he;q=0.6",
    'cookie': "checkcookie=yes; checkcookie=yes; _ga=GA1.4.1570175447.1446665076; LBONLINE40=1; CH40Request=bf5b6f22-7d51-4362-809e-e346b495919a; _dc_gtm_UA-37498201-17=1; NotAuthOnline40=1nnvhr5gtwfg0c2x34uqd2ne; ct2=t=2a1ca33a-a599-4050-8c28-12c9b607595e&it=2&i=0az+6sKUOzO4GRtEYPQdquNQmKf8XvoEx3WFTdyJFVI=; .AUTHONLINE40=5C303C9C7E651EB909079DEAB30C5979D9731E5B664BCB9D610AA13054B597697AD28EC42511BD91A8F0A1A067708A578D71F89252E3E344B355648003FE45FBFA661016E6C3ED3127DC7E9A8AEB9DF8FB5F13B37D1A6826ECA52624B232816D609C44B045BD9FFFFDF28A4529B8CFC95E70083A; WWW=REG%7c%d7%a2%d7%95%d7%93%d7%93; BenefitDetails=qTNGeAahrhvXeK1JIfh0fYpkhmsUheBitz6fZbuWTL4%2b1Gc%2f5S1pfIogFWQPXw8U1aAPA3HqhPz5%2bSYxLji1ec9O6Ak%2bL2GHMvW5hYO6v3AVPLcLGqFtNIpFdSDQWL%2f4; _ga=GA1.3.1570175447.1446665076",
    'cache-control': "no-cache",
    'postman-token': "1aa03d01-83c1-73b6-a073-833fcb36394f"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)