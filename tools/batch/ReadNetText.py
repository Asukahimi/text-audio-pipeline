import requests
from bs4 import BeautifulSoup

url = '<INTERNAL_TICKET_URL>'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
element = soup.find('第三里程碑', class_='user-info')
text = element.get_text()

print(text)
print('it finally works!')