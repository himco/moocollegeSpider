import json

import MySQLdb
from flask import Flask, render_template, request

app = Flask(__name__)
# 连接数据库
db = MySQLdb.connect("***", "***", "***", "***")


@app.route('/get')
def getInfo():
    keyword = request.args['key']
    if not keyword:
        return render_template("index.html")

    # 连接数据库
    db = MySQLdb.connect("yhsm88.cn", "mooc", "mooc", "mooc")

    cursor = db.cursor()
    cursor.execute("SELECT * FROM `spider` where "
                   "title like \'%" + keyword + "%\' or " +
                   "sz1 like \'%" + keyword + "%\' or " +
                   "sz2 like \'%" + keyword + "%\' or " +
                   "sz3 like \'%" + keyword + "%\' or " +
                   "sz4 like \'%" + keyword + "%\'")
    data = cursor.fetchall()
    resultList = list()
    # resultDict  = dict()
    # tmpStr = str()
    # tmpStr.find()

    for single in data:
        resultList.append(single)
        # print(single)

    # for ii in range(len(resultList)):
    #     tmpstr = str(resultList[ii])
    #     tmpstr = tmpstr.replace("http://", "<a href=\"http://") \
    #         .replace("https://", "<a href=\"https://") \
    #         .replace(".pdf'}", ".pdf'}\">点击下载</a>") \
    #         .replace(".zip'}", ".zip'}\">点击下载</a>") \
    #         .replace(".mp4'}", ".mp4'}\">点击下载</a>") \
    #         .replace(".doc'}", ".doc'}\">点击下载</a>") \
    #         .replace(".docx'}", ".docx'}\">点击下载</a>") \
    #         .replace(".jpg'}", ".jpg'}\">点击下载</a>") \
    #         .replace(".png'}", ".png'}\">点击下载</a>")
    #     print(tmpstr[0])
    # resultList[ii] = tuple(tmpstr)

    # resultDict["data"] = resultList
    return render_template('result.html', backdata=resultList)


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    db.close()
