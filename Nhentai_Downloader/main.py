import os
import eel
import xlwings as xw
from extension.CrawlerNhentai_ext import *

downloadpath = os.path.abspath('..') + '\\NDownload'
excelpath = os.path.abspath('..') + '\\NDownloader.xlsx'
covercachepath = os.path.abspath('.') + '\\NDownloader\\img\\covercache'
title_overall = '總覽'
title_category = '分類緩衝區'

idsArray = []
idsQueue = []
idsFinished = []
mangaFolder = {}


def createFolder(downloadpath):
    if not os.path.isdir(downloadpath):
        os.mkdir(downloadpath)
        print("createFolder")
    else:
        print(F'[ExistsError]: 資料夾已經存在')


def createCovercache(covercachepath):
    if not os.path.isdir(covercachepath):
        os.mkdir(covercachepath)
        print("createCovercache")
    else:
        print(F'[ExistsError]: 快取資料夾已經存在')


def createExcel(excelpath):
    if not os.path.isfile(excelpath):
        app = xw.App(visible=False, add_book=False)
        wb = app.books.add()
        wb.sheets.add()
        wb.sheets[0].name = title_overall
        wb.sheets[1].name = title_category
        sht0 = wb.sheets[0]
        sht = wb.sheets[1]
        print(sht0, sht)
        sht0.range('A1').column_width = 16
        sht0.range('B1:C1').column_width = 8.38
        sht0.range('A1').value = '已建表'
        sht0.range('B1').value = '建表數'
        sht0.range('C1').value = '=COUNTA(A$2:A$1000000)'
        sht0.range('A1:B1').color = (35, 115, 70)
        sht0.range('A1:B1').api.Font.Color = 0xFFFFFF
        sht0.range('A:C').api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter

        sht.range('A1').column_width = 12.75
        sht.range('B1').column_width = 16
        sht.range('C1').column_width = 99.38
        sht.range('D1').column_width = 8.25
        sht.range('E1:G1').column_width = 8.38
        sht.range('A1').value = '番號'
        sht.range('B1').value = '作者'
        sht.range('C1').value = '名稱'
        sht.range('D1').value = '頁數'
        sht.range('E1').value = '是否建表'
        sht.range('F1').value = '總本數'
        sht.range('G1').value = '=COUNTA(A$2:A$1000000)'
        sht.range('H1').value = '未紀錄數'
        sht.range('I1').value = '=COUNTA(A$2:A$1000000)-COUNTA(E$2:E$1000000)'
        sht.range('A1:F1,H1').color = (35, 115, 70)
        sht.range('A1:F1,H1').api.Font.Color = 0xFFFFFF
        sht.range('A:B,D:I').api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter
        wb.save(excelpath)
        app.quit()
        print("createExcel")
    else:
        print(F'[ExistsError]: Excel 已經存在')


if __name__ == '__main__':
    createFolder(downloadpath)
    createCovercache(covercachepath)
    createExcel(excelpath)


# =================================================
eel.init('NDownloader')


def startdownload(downloadpath, excelpath, title_category):
    app = xw.App(visible=False, add_book=False)
    wb = app.books.open(excelpath)
    osht = wb.sheets[title_overall]
    sht = wb.sheets[title_category]
    numauthors = osht.range('C1').options(numbers=int).value
    authors = osht.range(F'A2:A{numauthors+1}').value
    numbooks = sht.range('I1').options(numbers=int).value
    barcodes = sht.range(F'A2:A{numbooks+1}').options(numbers=int).value

    if(numbooks == 0):
        wb.save(excelpath)
        app.quit()
        return 0

    numbers = str(barcodes).strip('[]').split(', ')
    for book in numbers:
        source = 'https://nhentai.net/g/' + book

        headers = chooseHeader()  # 提供瀏覽器 header 資訊，讓網頁以為不是爬蟲
        try:
            Mangareq = rq.get(url=source, headers=headers, timeout=5)
        except RequestException:
            status.setdefault(book, "ReqError Occured")
            eel.showStatus(book, status[book])
            continue
        else:
            if Mangareq.status_code == 200:
                Mresult = Mangareq.text

        bookname, totalpage, author = getBookInfo(Mresult)  # 獲取名稱、頁數 # getBookInfo(Mresult, headers)
        fillBookInfo(book, sht, numbooks, bookname, totalpage, author)  # 自動填入作者、名稱、頁數
        eel.showDownloadInfo(bookname, totalpage, author)

        # 創建資料夾，並記錄每一本的路徑
        filepath, existsflag = createGalleryFolder(downloadpath, book, bookname)
        if existsflag == True:
            eel.showStatus(book, status[book])
            eel.DownloadFinished(None, book, 'False')
            continue
        mangaFolder.setdefault(book, filepath)

        # 下載較小張的封面作為預覽
        cover = getMangaCover(Mresult, headers, covercachepath, book)
        # print('covercachepath>>', covercachepath)
        eel.coverPreview(cover, book)
        eel.sleep(0.1)

        # Downloading =================================================================
        for i in range(1, int(totalpage)+1):
            ReqError = downloadIMG(i, source, headers, filepath, book, totalpage)
            if (ReqError == 'ReqError'):
                continue
            eel.progressBar(i, totalpage)
        # if the download is uncompleted, it should be recorded. (maybe use dict?)
        if (len(os.listdir(filepath)) >= int(totalpage)):
            status.setdefault(book, "completed")
            # print(F'[Finish] Total >> {len(os.listdir(filepath))} / {totalpage}')  # debug
            # print(F'Name >> {bookname}')  # debug
            # print('-' * 30)  # debug
        else:
            status.setdefault(book, "Incompleted")
            # print(F'[Incomplete] Total >> {len(os.listdir(filepath))} / {totalpage}')  # debug
            # print('-' * 30)  # debug
        with open(F'{filepath}\\{book}.txt', 'w'):
            pass
        # ============================================================================
        eel.DownloadFinished(cover, book, 'True')
    checkRecord(sht, numbooks, authors)
    wb.save(excelpath)
    app.quit()

    eel.showStatus('Status', '[ Total ]')
    eel.showStatus('--------', '---------')
    for status_key, status_value in status.items():
        eel.showStatus(status_key, status_value)

    eel.TotalFinished()
    status.clear()


@eel.expose  # In JS function "getGalleryID()"
def getIdsArray(idsValue):
    idsArray.append(idsValue)
    print(idsArray)  # test


@eel.expose  # In JS function "getGalleryID()"
def galleryDownload():
    global idsArray, downloadpath, excelpath, title_category

    # idsArray = [i for i in idsArray if (len(i) == 6)]
    idsArray.reverse()
    if len(idsArray) == 0:
        eel.TotalFinished()
        return 0

    app = xw.App(visible=False, add_book=False)
    wb = app.books.open(excelpath)
    sht = wb.sheets[title_category]
    for i in idsArray:
        # print(F"{idsArray.index(i)+1}. {i}")  # test
        sht.range('A2:E2').insert(shift='down', copy_origin='format_from_right_or_below')
        sht.range('A2').value = F'{i}'
    sht.range('G1').value = '=COUNTA(A$2:A$1000000)'
    sht.range('I1').value = '=COUNTA(A$2:A$1000000)-COUNTA(E$2:E$1000000)'
    wb.save(excelpath)
    app.quit()
    idsArray.clear()

    startdownload(downloadpath, excelpath, title_category)


@eel.expose  # In JS function "toggleFbtn()"
def openOverallDir():
    os.startfile(downloadpath)


@eel.expose  # In JS function "toggleEbtn()"
def openExcel():
    os.startfile(excelpath)


@eel.expose  # In JS function "toggleIbtn()"
def openMangaFolder(book):
    os.startfile(mangaFolder[book])


@eel.expose  # In JS function "toggleIbtn()"
def ClnCovercache():
    if (len(os.listdir(covercachepath)) == 0):
        return 0
    else:
        mangaFolder.clear()
        for i in os.listdir(covercachepath):
            if i.endswith('.jpg'):
                try:
                    os.remove(covercachepath + '\\' + i)
                except Exception:
                    continue


eel.start('main.html', position=(0, 540))
