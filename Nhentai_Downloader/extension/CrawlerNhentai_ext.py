import os
import requests as rq
from requests.exceptions import RequestException, Timeout, HTTPError
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs

status = {}


def chooseHeader():
    user_agent = UserAgent()
    header = {'User-Agent': user_agent.random}
    return header


def getBookInfo(Mresult):
    html = bs(Mresult, 'html.parser')
    bookname = html.select('h2')[0].get_text()
    totalpage = html.select('span.name')[-1].get_text()
    author = html.select('span.before')[-1].get_text()

    try:
        author = author.split('[')[1].split(']')[0]
    except:
        author = '###'
    else:
        if (author.find('(', 0, len(author)) != -1):
            author = author.split('(')[-1].split(')')[0]
    return bookname, totalpage, author


def fillBookInfo(book, sht, numbooks, bookname, totalpage, author):
    for i in range(2, numbooks + 2):
        index = str(sht.range(F'A{i}').options(numbers=int).value)
        if (index == book):
            sht.range(F'B{i}').value = author
            sht.range(F'C{i}').value = bookname
            sht.range(F'D{i}').value = totalpage


def checkRecord(sht, numbooks, authors):
    for i in range(2, numbooks + 2):
        author = sht.range(F'B{i}').value
        if author in authors:
            sht.range(F'E{i}').value = '已建表'
        else:
            sht.range(F'E{i}').value = '未建表'


def createGalleryFolder(downloadpath, book, bookname):
    filepath = F'{downloadpath}\\{bookname}'
    existsflag = False
    if not os.path.isdir(filepath):
        try:
            os.mkdir(filepath)
        except:
            try:
                filepath = F'{downloadpath}\\{book}'
                os.mkdir(filepath)
            except (Exception, FileExistsError) as e:
                error_class = e.__class__.__name__
                existsflag = True
                status.setdefault(book, error_class + ', skip')
                print(F'[{error_class}]: 檔案已經存在 or 路徑出現錯誤，跳過下載')  # debug
                print('—' * 30)  # debug
                return filepath, existsflag
    else:
        existsflag = True
        status.setdefault(book, "Existed, skip")
        print(F'[FileExistsError]: 檔案存在，跳過下載')  # debug
        print('—' * 30)  # debug
        return filepath, existsflag

    return filepath, existsflag


def getMangaCover(Mresult, headers, covercachepath, book):
    html = bs(Mresult, 'html.parser')
    coverurl = html.select('img.lazyload')[0].get('data-src')

    try:
        with rq.get(url=coverurl, headers=headers, stream=True, timeout=5) as r:
            blockSize = 1024
            with open(F'{covercachepath}\\{book}.jpg', 'wb') as f:
                for data in r.iter_content(blockSize):
                    f.write(data)
    except Timeout:
        status.setdefault(book, "Timeout Occured")
        print('[Timeout] Download failed.')  # debug
    except HTTPError as herr:
        status.setdefault(book, "HTTPError Occured")
        print(F'[HTTPError] {herr}')  # debug
    except RequestException:
        status.setdefault(book, "ReqError Occured")
        print('[RequestException] Error Occured.')  # debug

    return './img/covercache/'


def downloadIMG(i, source, headers, filepath, book, totalpage):
    url = source + '/' + str(i)
    try:
        req = rq.get(url=url, headers=headers, timeout=5)
    except RequestException:
        status.setdefault(book, F"-{i} ReqError")
        print(F'IMG.{i:<3d} : RequestException Occured.')  # debug
        return 'ReqError'
    else:
        if req.status_code == 200:
            result = req.text
            html = bs(result, 'html.parser')
            img = html.select('section#image-container img')[0]
            imgurl = img.get('src')

    tryTimes = 0
    while(tryTimes < 3):
        try:
            with rq.get(url=imgurl, headers=headers, stream=True, timeout=5) as r:
                blockSize = 1024
                with open(F'{filepath}\\{str(i)}.jpg', 'wb') as f:
                    for data in r.iter_content(blockSize):
                        f.write(data)
            break

        except Timeout:
            tryTimes += 1
            if tryTimes == 3:
                status.setdefault(book, F"-{i} Timeout")
                print(F'\rIMG.{i:<3d} : [Timeout] Retry for {tryTimes} times.')  # debug
        except HTTPError as herr:
            status.setdefault(book, F"-{i} HTTPError")
            print(F'IMG.{i:<3d} : {herr}')  # debug
            break
        except RequestException:
            status.setdefault(book, F"-{i} ReqError")
            print(F'IMG.{i:<3d} : RequestException Occured.')  # debug
            break
