import requests
from bs4 import BeautifulSoup
import mysql.connector


def parse_index(url):
    '''
    解析索引页面
    返回图书所有信息
    '''
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print('error:', e)


def parse(text):
    '''
    解析图书详细信息
    '''
    soup = BeautifulSoup(text.strip(), 'lxml')
    books = soup.select('.item')
    info = {}
    for book in books:
        info.clear()
        info['title'] = book.select('.pl2 a')[0].get_text(
        ).strip().replace(' ', '').replace('\n', '')
        info['author'] = book.select(
            '.pl')[0].get_text().strip().split('/')[0].strip()
        info['publishers'] = book.select(
            '.pl')[0].get_text().strip().split('/')[-3].strip()
        info['date'] = book.select(
            '.pl')[0].get_text().strip().split('/')[-2].strip()
        info['price'] = book.select(
            '.pl')[0].get_text().strip().split('/')[-1].strip()
        info['star'] = float(book.select('.rating_nums')[0].get_text())
        info['summary'] = book.select('.inq')[0].get_text(
        ).strip() if book.select('.inq') else ''
        yield info


def open_mysql():
    '''
    连接mysql
    '''
    cnx = mysql.connector.connect(user='minutesheep', database='douban')
    cursor = cnx.cursor()
    return cnx, cursor


def save_to_mysql(cnx, cursor, info):
    '''
    将数据写入mysql
    '''
    add_book_top250 = ("INSERT IGNORE INTO book_top250 "
                       "(title,author,publishers,date,price,star,summary) "
                       "VALUES (%(title)s, %(author)s, %(publishers)s, %(date)s, %(price)s, %(star)s, %(summary)s)")

    cursor.execute(add_book_top250, info)
    cnx.commit()


def close_mysql(cnx, cursor):
    '''
    关闭mysql
    '''
    cursor.close()
    cnx.close()


def main():
    base_url = 'https://book.douban.com/top250?start='
    cnx, cursor = open_mysql()
    for page in range(0, 250, 25):
        index_url = base_url + str(page)
        text = parse_index(index_url)
        info = parse(text)
        for result in info:
            save_to_mysql(cnx, cursor, result)
    close_mysql(cnx, cursor)


if __name__ == '__main__':
    main()
