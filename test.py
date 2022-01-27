import requests
import os
import re
from tqdm import tqdm
import pandas as pd
import datetime as dt

from bs4 import BeautifulSoup
from lxml.html import fromstring

def get_cnt(url):
    response = requests.get(url)

    if(response.status_code == 200):
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        cnt = soup.select_one('#old_content > h5 > div > strong').get_text()
        print(cnt)
    else:
        print(response.status_code)
        cnt = -1
    return cnt

def get_comments(page_num, url):
    url = url[:-1]
    comments = []
    feels = []
    for i in tqdm(range(1, page_num+1)):
        res = requests.get(url + str(i))
        parser = fromstring(res.text)        
        for j in range(1, 10):
            try:
                score = parser.xpath('//*[@id="old_content"]/table/tbody/tr[{}]/td[2]/div/em'.format(j))[0].text_content()
                if int(score)>=9 or int(score)<=2:
                    texts = parser.xpath('//*[@id="old_content"]/table/tbody/tr[{}]/td[2]/text()'.format(j))
                    for text in texts:
                        if isHangul(text):
                            comments.append(re.sub(r'[\t\n]',"",text))
                            if int(score)>=9:
                                feels.append(1)
                            else:
                                feels.append(0)
            except:
                print('error')
    return feels, comments

def isHangul(text):
    #https://github.com/chandong83/python_hangul_check_function
    hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
    return hanCount > 0

def main():
    f_url = 'https://movie.naver.com/movie/point/af/list.naver?&page=1'
    now = dt.datetime.now()
    cnt = get_cnt(f_url)
    page_cnt = int(cnt)//10
    feels, comments = get_comments(100000, f_url)
    df = pd.DataFrame([i for i in zip(feels, comments)])
    #pandas 한글 깨짐
    #https://dolhani.tistory.com/521
    df.to_csv(os.path.join(local_path, 'data', 'nsmc_{}{}{}.csv'.format(str(now.year)[-2:], str(now.month), str(now.day))), encoding='utf-8-sig')
    print(df.shape)

if __name__ == '__main__':
    local_path = os.getcwd()
    main()