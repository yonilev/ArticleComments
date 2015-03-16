#encoding=utf8
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import pickle



def download_ynet_html(driver,url):
    try:
        tries = 0
        while tries<3:
            tries+=1
            try:
                driver.get(url)
                break
            except Exception,e:
                print str(e)
        #wait for page to load
        time.sleep(1)
        element = driver.find_element_by_id("stlkbcopenalldiv")
        element.click()        
        #wait for click to load
        time.sleep(2)
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    except Exception,e:
        print str(e)
        return None
    return html



class Comment:
    def __init__(self,author_location,date,title,body,score):
        self.author_location=author_location
        self.date=date
        self.title=title
        self.body=body
        self.score=score

class Page:
    def __init__(self,url,title,subtitle,body,author,published_time,categories,tags,comments):
        self.url = url
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.author = author
        self.published_time = published_time
        self.categories = categories
        self.tags = tags
        self.comments = comments
        
        
def parse_ynet_page(driver,url):
    html = download_ynet_html(driver,url)
    if html==None:
        return None
    soup = BeautifulSoup(html)

    #title of the article
    title = soup.find('div',{ "class" : "art_header_title" }).text
    #subtitle of the article
    subtitle = soup.find('div',{ "class" : "art_header_sub_title" }).text
    #body of article
    body_element = soup.find('div',{'class':'art_body_width_3'})
    body = '\n'.join([p.text for p in body_element.find_all('p')])
    #author of the article
    author_element = soup.find_all('span',{ "class" : "art_header_footer_author" })
    author = author_element[0].text
    #time of publication
    published_time = author_element[1].text
    published_time = re.search(r'\d\d\.\d\d\.\d\d , \d\d:\d\d',published_time).group(0)
    published_time = time.strptime(published_time, "%d.%m.%y , %H:%M")
    #category and subcategory of the article
    category_element = soup.find('ul',{ "class" : "trj_trajectory" }) 
    categories = [c.text for c in category_element.children]
    #tags of articles
    tags = [e.text for e in soup.find_all('a',{ "class" : "articletags_link" }) ]
    
    
    #comments of article
    comments = []
    while True:
        try:
            comments_element = soup.find('div',{ "class" : "art_tkb_talkbacks" })
            for e in comments_element.children:
                author_location_date = e.find('div',{ "class" : "art_tkb_name_location_date" }).text
                comment_date = re.search(r'.*?\(.*?(\d{2}\.\d{2}\.\d{2}).*?\)',author_location_date).group(1)
                comment_date = time.strptime(comment_date, "%d.%m.%y")
                comment_author_location = re.sub(r'\(.*?\)','',author_location_date).strip()
                comment_title = e.find('span',{ "class" : "art_tkb_talkback_title" }).text
                comment_title = re.sub(r'\(..\)','',comment_title).strip()
                comment_body_element = e.find('div',{ "class" : "art_tkb_talkback_content art_tkb_talkback_content_visible" })
                if comment_body_element!=None:
                    comment_body = comment_body_element.text
                else:
                    comment_body = ''
                comment_score = int(e.find('div',{ "class" : "art_tkb_recmm_wrapper" }).text)
                comments.append(Comment(comment_author_location,comment_date,comment_title,comment_body,comment_score))
            element = driver.find_element_by_id("stlkbcnexttalkbacks")
            element = element.find_element_by_tag_name('a')
            element.click()      
            time.sleep(2)
            html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            soup = BeautifulSoup(html)
        except Exception,e:
            break
    
    p = Page(url,title,subtitle,body,author,published_time,categories,tags,comments)
    return p

def download_ynet_pages(file_ind,url_ind):
    driver = webdriver.PhantomJS(executable_path='C:/Program Files/phantomjs-2.0.0-windows/bin/phantomjs.exe') 
    url_format = 'http://www.ynet.co.il/articles/0,7340,L-{0},00.html'
    while True:
        url = url_format.format(url_ind)
        print file_ind,url
        try:
            p = parse_ynet_page(driver,url)
            if p!=None:
                with open('data/{0}.pkl'.format(file_ind), 'w') as outfile:
                    pickle.dump(p, outfile)
                print 'success\n'
                file_ind+=1
        except Exception,e:
            print str(e)
        url_ind-=1
       

#download_ynet_pages(2194,4628958)