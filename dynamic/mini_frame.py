# import time
#
# def login():
#     return "hahah"
#
# def register():
#     pass
#
# def profile():
#     pass
#
# def application(file_name):
#     if file_name == "/login.py":
#         return login()
#     elif file_name == "/register.py":
#         return register()
#     else:
#         return "not found you page"
import re
from pymysql import *
import urllib.parse
import logging

URL_FUNC_DICT = dict()

def route(url):
    def set_func(func):
        # URL_FUNC_DICT['/index.py'] = index
        URL_FUNC_DICT[url] = func
        def call_func(*args, **kwargs):
            return  func(*args, **kwargs)
        return call_func
    return set_func

@route("/index.html")
def index(ret):
    #因为运行的是http服务器.py所以open的路径就是以http服务器.py的地址算
    with open("/home/zzy/套接字/web服务器/templates/index.html") as f:
        content = f.read()
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='1995', charset='utf8')
    cs = conn.cursor()
    cs.execute("select * from info;")
    stock_infos = cs.fetchall()
    cs.close()
    conn.close()

    tr_templete = """<tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
        </td>
        </tr>
    """
    html = ""
    for line_info in stock_infos:
        html += tr_templete % (line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6], line_info[7], line_info[1])

    content = re.sub(r"\{%content%\}", html, content)
    return content

@route("/center.html")
def center(ret):
    with open("/home/zzy/套接字/web服务器/templates/center.html") as f:
        content = f.read()

    conn = connect(host='localhost', port=3306, user='root', password='1995', database='stock_db', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    cs.execute(
        "select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;")
    stock_infos = cs.fetchall()
    # print(cs.fetchall())
    cs.close()
    conn.close()

    tr_template = """
           <tr>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>
                   <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
               </td>
               <td>
                   <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
               </td>
           </tr>
       """

    html = ""
    for line_info in stock_infos:
        html += tr_template % (
        line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6],line_info[0], line_info[0])

    # content = re.sub(r"\{%content%\}", str(stock_infos), content)
    content = re.sub(r"\{%content%\}", html, content)
    # print(content)
    return content

@route("/update/(\d+)\.html")
def update(ret):
    stock_code = ret.group(1)
    with open("/home/zzy/套接字/web服务器/templates/update.html") as f:
        content = f.read()
    conn = connect(host='localhost', port=3306, user='root', password='1995', database='stock_db', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    sql = "select f.note_info from focus as f inner join info as i on i.id=f.info_id where i.code = %s;"
    cs.execute(sql, (stock_code,))
    stock_infos = cs.fetchone()
    note_info = stock_infos[0]  # 获取这支股票对应的备注信息
    cs.close()
    conn.close()
    content = re.sub(r"\{%note_info%\}", note_info, content)
    content = re.sub(r"\{%code%\}", stock_code, content)
    return content

@route("/update/(\d+)/(.*)\.html")
def save_update_page(ret):
    stock_code = ret.group(1)
    comment = ret.group(2)
    comment = urllib.parse.unquote(comment)
    sql = """update focus set note_info = "%s" where info_id = (select id from info where code = %s);"""
    conn = connect(host='localhost', port=3306, user='root', password='1995', database='stock_db', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    cs.execute(sql, (comment, stock_code))
    conn.commit()
    cs.close()
    conn.close()
    return "修改成功..."
# URL_FUNC_DICT = {
#     '/index.py':index,
#     '/center.py':center
# }
# 给路由添加正则表达式的原因：在实际开发时，url中往往会带有很多参数，例如/add/000007.html中000007就是参数，
# 如果没有正则的话，那么就需要编写N次@route来进行添加 url对应的函数 到字典中，此时字典中的键值对有N个，浪费空间
# 而采用了正则的话，那么只要编写1次@route就可以完成多个 url例如/add/00007.html /add/000036.html等对应同一个函数，此时字典中的键值对个数会少很多
@route(r"/add/(\d+)\.html")
def add_focus(ret):
    # 获取股票代码
    stocke_code = ret.group(1)
    # 判断试下是否有这个股票代码
    conn = connect(host='localhost', port=3306, user='root', password='1995', database='stock_db', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    sql = "select * from info where code = %s;"
    # 防止sql注入，sql放在execute里面拼接
    cs.execute(sql, (stocke_code,))
    stock_infos = cs.fetchone()
    # 如果没有股票代码
    if not stock_infos:
        cs.close()
        conn.close()
        return "没有这支股票"

    # 判断一下是否已经关注过
    sql = "select * from info as i inner join focus as f on i.id = f.info_id where i.code = %s;"
    cs.execute(sql, (stocke_code,))
    # 如果查出来了表示已经关注过
    print(sql)
    if cs.fetchone():
        cs.close()
        conn.close()
        print(stocke_code)
        return "已经关注过"

    # 添加关注
    sql = "insert into focus (info_id) select id from info where code = %s;"
    cs.execute(sql, (stocke_code,))
    conn.commit()
    cs.close()
    conn.close()
    return "关注成功"

@route(r"/del/(\d+)\.html")
def del_focus(ret):
    # 获取股票代码
    stocke_code = ret.group(1)
    # 判断试下是否有这个股票代码
    conn = connect(host='localhost', port=3306, user='root', password='1995', database='stock_db', charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    sql = "select * from info where code = %s;"
    # 防止sql注入，sql放在execute里面拼接
    cs.execute(sql, (stocke_code,))
    stock_infos = cs.fetchone()
    # 如果没有股票代码
    if not stock_infos:
        cs.close()
        conn.close()
        return "没有这支股票"

    # 判断一下是否已经关注过
    sql = "select * from info as i inner join focus as f on i.id = f.info_id where i.code = %s;"
    cs.execute(sql, (stocke_code,))
    # 如果查出来了表示已经关注过

    if not cs.fetchone():
        cs.close()
        conn.close()
        print(stocke_code)
        return "没有关注过"

    # 取消关注
    sql = "delete from focus where info_id = (select id from info where code = %s);"
    cs.execute(sql, (stocke_code,))
    conn.commit()
    cs.close()
    conn.close()
    return "取消关注成功"

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    file_name = env['PATH_INFO']
    # if file_name == "/center.py":
    #     return center()
    # elif file_name == "/index.py":
    #     return index()
    # else:
    #     return 'Hello World!'
    logging.basicConfig(level=logging.WARNING,
                        filename='./log.txt',
                        filemode='w',
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.info("访问的是， %s" % file_name)

    try:
        for url, func in URL_FUNC_DICT.items():
            ret = re.match(url, file_name)
            if ret:
                return func(ret)
        else:
            logging.warning("没有对应的函数")
            return "请求的url(%s%s)没有对应的函数...." % (file_name, url)
    except Exception as ret:
        return "产生了异常 %s" % str(ret)
