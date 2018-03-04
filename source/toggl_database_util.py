
import datetime
import sys
import pickle
from .date_conv import todaysStr, yesterdaysStr, todaysDatetime, str2Datetime, str2Date, calcDurMin

def extractLatestDate(database):
	latestdate = database[-1]["start"]
	return latestdate

def readTogglDB(filename):
	try:
		with open(filename,"rb") as f:
			database = pickle.load(f)
			print("データベースファイルが存在しました。")
		return database
	except:
		print("データベースファイルが存在しません。")
		return None

def judgeLatest(database):
	today_dt  = todaysDatetime()
	latest_dt = extractLatestDate(database)
	diff = today_dt - latest_dt
	latestFlag = False
	#現在時間と最新タスクの開始時間が24時間以上ずれていたらデータベースを更新する。
	if diff.total_seconds() < 24*60*60:
		latestFlag = True
	#latestFlag = False #hack: Falseが返るようにすると実行の度にデータベースが更新される
	return latestFlag

def generateTogglDB(tw):
	todaysstr = todaysStr()
	raw_database = tw.fetchPeriodData(until="2017-04-30")
	database = info_reduce(raw_database)
	return database

def addTogglDB(database_old, tw):
	latest_dt = extractLatestDate(database_old)
	yesterdays_str = yesterdaysStr()
	update_period = 7 #最新のタスクのupdate_period日前から昨日までを更新する
	#読み込み開始位置を定義
	read_start = latest_dt + datetime.timedelta(days = (1-update_period))
	read_start_str = read_start.strftime('%Y-%m-%d')
	read_start = datetime.datetime.strptime(read_start_str,'%Y-%m-%d')
	#カット位置を計算
	read_pos = 0
	for i, ele in enumerate(database_old):
		if ele["start"]>read_start:
			read_pos = i
			break
	#更新される部分をカット
	database_old = database_old[:read_pos]
	#更新分のデータを取ってくる
	raw_database = tw.fetchPeriodData(since=read_start_str,until=yesterdays_str)
	#更新分データの情報削減
	database_new = info_reduce(raw_database)
	#元のデータと更新分データを足して返す
	database_new = database_old + database_new
	return database_new

def updateTogglDB(filename, tw):
	database = readTogglDB(filename)
	if database == None: #データベースが存在しないばあい
		database = generateTogglDB(tw)
	else: #データベースが存在した場合
		if judgeLatest(database) == True:	#データベースが最新の場合
			print("データベースは最新版です")
		else:	#データベースが最新ではない場合、データを追加
			print("データベースを最新版に更新します")
			database = addTogglDB(database, tw)
	#データベースをpickleに書き込み
	with open(filename,"wb") as f:
		pickle.dump(database, f)
	#その後の処理に使うためにデータベースを返す
	return database

def info_reduce(raw_database):
	database = []
	key_ls = ['id','pid','description','start','end','dur','client','project','tags']
	for task in raw_database:
		new_task = {}
		for key in key_ls:
			ele = task[key]
			if (key == 'start') or (key == 'end'):
				ele = str2Datetime(ele)
			new_task[key] = ele
		database.append(new_task)
	return database

#データベースの一部を取ってくる [toggl_database_util]
def cut_database(database, since_str, until_str=None):
	since_date = str2Date(since_str)
	new_database = []
	if until_str != None:
		until_date = str2Date(until_str)+datetime.timedelta(days = 1)
	else:
		until_date = str2Date(todaysStr())
	for data in database:
		tmp_time = data["start"]
		if (tmp_time>since_date) and (tmp_time<until_date):
			new_database.append(data)
	return new_database