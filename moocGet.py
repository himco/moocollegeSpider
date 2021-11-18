import requests
import hashlib
import xlsxwriter as xw
import time
import signal, sys
import threading


class MoocSpider:
    def __init__(self, howlong=5000, rangeFrom=150000, rangeTo=229329):
        # 捕获系统事件
        signal.signal(signal.SIGTERM, self.termSigHandler)
        signal.signal(signal.SIGINT, self.termSigHandler)
        self.isCatched = False  # 捕获事件

        # 划分步长
        self.howlong = howlong

        # 作品id遍历范围
        self.rangeFrom = rangeFrom
        self.rangeTo = rangeTo

        # 导出表格参数
        self.workbook = xw.Workbook('export%s-%s_%s.xlsx' % (
            self.rangeFrom, self.rangeTo, time.strftime('%Y-%m-%d %H-%M', time.localtime(time.time()))))
        self.worksheet = list()
        self.currentRow = list()
        self.thread_num = 0
        self.thread_list = list()

        # 划分数据(每5000划一个线程)
        cycle_times = (rangeTo - rangeFrom) / self.howlong + 1
        for nn in range(int(cycle_times)):
            start_ = nn * self.howlong + rangeFrom
            end_ = start_ + self.howlong

            if nn == int(cycle_times - 1):  # 最后部分的数据处理
                end_ = int((cycle_times - int(cycle_times)) * self.howlong + start_)

            # print(start_, end_)

            # 新建子表和行索引
            worksheet_name = "%d-%d" % (start_, end_)
            self.worksheet.append(self.workbook.add_worksheet(worksheet_name))
            self.currentRow.append(0)

            # 开始线程
            self.thread_list.append(
                threading.Thread(target=self.thread_work,
                                 name='t%d' % self.thread_num,  # 线程名字
                                 args=(start_, end_))
            )
            self.thread_list[-1].start()
            self.thread_num += 1

        while True:
            if threading.active_count() == 1:  # 只剩下主线程了
                print('线程结束')
                # 关闭工作表
                self.workbook.close()
                break

    def thread_work(self, from_, to_):
        # print(sheet_name,from_,to_)
        worksheet_idx = threading.current_thread().name[-1]

        # 开始获取数据
        for idx in range(from_, to_):
            if self.isCatched:  # 如果捕获到了中止
                print('[t%d]线程中止...' % int(worksheet_idx))
                break
            else:
                # print('[t%d]线程running...' % int(worksheet_idx))
                jsonData = self.getApiData(str(idx))
                self.parseJson(idx,
                               int(worksheet_idx),
                               99 - (to_ - idx) / (to_ - from_) * 100,
                               jsonData)
                pass
        # print()
        # pass

    def termSigHandler(self, signum, frame):
        print('捕获事件')
        self.isCatched = True

    def getApiData(self, workId):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53',
            'pragma': 'no-cache'
        }

        tmpErrorData = dict()
        tmpErrorData['code'] = -1
        try:
            back_data = requests.get(url="https://cc.moocollege.com/api/review/share/pool?mdPoolId=" +
                                         hashlib.md5(workId.encode('utf-8')).hexdigest(),
                                     headers=headers, timeout=8)
        except:
            return tmpErrorData
        return back_data.json()

    def parseJson(self, currentId, sheetIdx, percentage, jsonData):
        if jsonData.get('code') == None and jsonData.get('code') != 0:
            print('[t%d-%6d-%3d%%]作品不存在' % (sheetIdx, currentId, percentage))
        elif jsonData.get('code') == 0:
            col = 0  # 列
            try:
                jsonData = jsonData.get('data')

                if jsonData is None:
                    return
                # print(jsonData)

                print('[t%d-%6d-%3d%%]Get:%s-%s-%s-%s' % (sheetIdx,
                                                          currentId,
                                                          percentage,
                                                          jsonData['title'],
                                                          jsonData['authorName'],
                                                          jsonData['school'],
                                                          jsonData['competitionId']))

                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col, '%d' % currentId)  # 作品编号
                col += 1

                # 作品概要
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s-%s' % (jsonData['title'], jsonData['titleEn']))  # title&En
                col += 1
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s' % (jsonData['createTime']))  # createTime
                col += 1
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s' % jsonData['competitionId'])  # competitionId
                col += 1
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s' % jsonData['rowName'])  # rowName
                col += 1
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s' % jsonData['authorName'])  # authorName
                col += 1
                self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                                               '%s' % jsonData['school'])  # school
                col += 1

                # self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col,
                #                                '%s' % jsonData['school'])  # test
                # col += 1

                # 作品详情
                jsonData = jsonData['infoObj']['attachList']  # infoObj
                for every in range(len(jsonData)):
                    everyData = jsonData[every]
                    '''
                    attachName 设计文档（pdf格式）
                    fileList
                    '''

                    if everyData['attach']:
                        self.worksheet[sheetIdx].write(self.currentRow[sheetIdx], col + every,
                                                       '%s:%s' % (everyData['attachName'], everyData['fileList']))
                        # print(jsonData[every])
                self.currentRow[sheetIdx] += 1  # 对行+1

            except BaseException as err:
                # print('[Error]',currentId, jsonData)
                print('[Error]', currentId, hashlib.md5(str(currentId).encode('utf-8')).hexdigest(), err)


if __name__ == '__main__':

    '''
    1: 220000 - 229329(2021-11-17 19:10最后一个作品)
    1: 220000 - 228000
    2: 228000 - 229329
    3: 150000 - 229329
    '''

    if len(sys.argv) != 4:
        print('请输入参数：1:howlong线程步长(5000) 2:from(作品编号起始) 3:to(结束)\n'
              'e.g. python moocGet.py 5000 220000 229329\n'
              'w: 线程数好像只能最高10个')
    else:
        MoocSpider(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
