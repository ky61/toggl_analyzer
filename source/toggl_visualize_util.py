
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

#日付・時間を扱う関数群 [date_conv.py]
from .date_conv import str2Datetime
#特定のタスクに使っている時間を計算 [analyzer.py]
from .analyzer import countTimeForParticularTasks
#データベースの一部を取ってくる [toggl_database_util]
from .toggl_database_util import cut_database

#1日の中での時間の使い方の描画 [toggl_visualize_util]
def drawTimeline(database, start_date_str, end_date_str, saveFlag=False):
	#領域を塗る色の定義
	col_dict = {
		"第一領域": "#890000",
		"第二領域": "#4bc800",
		"第三領域": "#fb8b14",
		"第四領域": "#3750b5",
		None: "#888888",
		}
	#日付文字列のdatetimeへの変換
	start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
	end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d') + datetime.timedelta(days = 1)
	#データベースの一部を取ってくる [toggl_database_util]
	sub_database = cut_database(database,since_str=start_date_str,until_str=end_date_str)
	#X軸の定義
	days_num = int((end_date-start_date).total_seconds()/60/60/24)
	dt_0 = str2Datetime(start_date_str+"T00:00:00+")
	dt_ls = [dt_0+datetime.timedelta(days = delta_day) for delta_day in range(days_num)]
	#描画部
	ax = plt.subplot()
	ax.grid(True)
	drawWeekendBand(dt_ls,ax) #土日を表す帯を描画 [toggl_visualize_util]
	time_range_daily = 20 #24ではぎゅぎゅうになる
	for one_task in sub_database:
		#開始日、開始時間の取得
		dt_start = one_task['start']
		h = dt_start.hour
		m = dt_start.minute
		s = dt_start.second
		dt_start_day = dt_start - datetime.timedelta(hours=h,minutes=m,seconds=s)
		dt_start_time_sec = (dt_start - dt_start_day)
		dt_start_hour = dt_start_time_sec.total_seconds()/60/60
		#終了日、終了時間、取得
		dt_end = one_task['end']
		#かかった時間の取得
		time_dur = dt_end - dt_start
		time_dur_hour = time_dur.total_seconds()/60/60
		dt_end_hour = dt_start_hour + time_dur_hour
		#クライアント(領域)の取得
		name_cli = one_task['client']
		#タスク情報に応じて四角形を塗る
		drawOnetask(ax, dt_start_day, dt_start_hour, dt_end_hour, col=col_dict[name_cli], width=20)
	ax.set_ylim(0,24)
	ax.set_xlim(start_date , end_date) # 範囲指定
	if saveFlag:
		figname = "graph_output/Timeline_"+start_date_str+"_"+end_date_str+".png"
		plt.savefig(figname)
	plt.show()

#タスク情報に応じて四角形を塗る [toggl_visualize_util]
def drawOnetask(ax, dt_start_day, dt_start_hour, dt_end_hour, col="#333333", width=20):
	left_edge  = dt_start_day - datetime.timedelta(hours=width/2)
	right_edge = dt_start_day + datetime.timedelta(hours=width/2)
	x = [left_edge, right_edge]
	y1 = dt_start_hour
	y2 = dt_end_hour
	ax.fill_between(x, y1, y2, facecolor=col) #y1とy2に囲まれた部分を塗る
	if dt_end_hour > 24.0: #24時を超えた場合は翌日にもう一つ四角をつくって塗る
		x = [left_edge+datetime.timedelta(days=1), right_edge+datetime.timedelta(days=1)]
		y1 = 0
		y2 = dt_end_hour-24
		ax.fill_between(x, y1, y2, facecolor=col) #y1とy2に囲まれた部分を塗る


#各領域にどれくらい使っているか三角グラフにより可視化 [toggl_visualize_util]
def drawQuadrant(database,
			three_region_ls=["第一領域", "第二領域", "第三領域"],
			group="month",
			saveFlag=False):
	from source.date_conv import returnMidnightDatetime
	#グラフの枠線を変える
	import matplotlib as mpl
	mpl.rc('axes', facecolor='none',edgecolor="none",titlesize=30,labelsize=15,grid=False)
	base_dt = None
	#クライアント名と配列の番地との対応を定義
	cli2num_dic = {"第一領域":0, "第二領域":1, "第三領域":2, "第四領域":3, None:4}
	#データベースの最初のタスクと最後のタスクの日付を抽出し間の日数を計算
	st_mid_dt = returnMidnightDatetime(database[0]["start"])
	en_mid_dt = returnMidnightDatetime(database[-1]["start"])
	days_num = int((en_mid_dt-st_mid_dt).total_seconds()/60/60/24)+1
	#各日付と各クライアントの2軸の配列を定義
	hour_per_client_ls = np.zeros((days_num,5))
	#配列にデータを格納していく
	for data in database:
		temp_dt = returnMidnightDatetime(data["start"])
		#最初のタスクの日を基準とする
		if base_dt == None: base_dt = temp_dt
		day_ind = int((temp_dt-base_dt).total_seconds()/60/60/24)
		cli_ind = cli2num_dic[data["client"]]
		#タスクにかかった時間
		dur_h = data["dur"]/1000/60/60
		hour_per_client_ls[day_ind][cli_ind] += dur_h
	#グループに関する情報を格納
	group_info_ls = []
	for day_ind in range(days_num):
		temp_dt = base_dt + datetime.timedelta(days=day_ind)
		temp_youbi = temp_dt.weekday()
		temp_year = temp_dt.year
		temp_month = temp_dt.month
		temp_day = temp_dt.day
		temp_dict = {
					 "year":temp_year,
					 "month":temp_month,
					 "day":temp_day,
					 "youbi":temp_youbi}
		group_info_ls.append(temp_dict)

	#描画部分。三角グラフ用モジュールをインポート
	import ternary
	fig, ax= ternary.figure(scale=100)
	ax.set_title("Scatter Plot", fontsize=20)
	ax.boundary(linewidth=2.0)
	ax.gridlines(multiple=5, color="gray")
	#ラベルごとに色を変えるべく、カラーマップを設定
	import matplotlib
	cmap = matplotlib.cm.get_cmap('terrain')

	ratio_ls = []
	label_ls = []
	th = 10 #th時間以上記録できていない日は描画しない
	for ind, daily in enumerate(hour_per_client_ls):
		daily_three = [daily[cli2num_dic[region]] for region in three_region_ls] 
		daily_three_total_hour = np.sum(daily_three)
		if daily_three_total_hour < th: continue
		daily_ratio = daily_three/(daily_three_total_hour/100)
		#print(daily_ratio)
		ratio_ls.append(daily_ratio)
		#ラベルの定義
		label = group_info_ls[ind][group]
		label_ls.append(label)
	ratio_ls = np.array(ratio_ls)
	#print(ratio_ls)
	#print(label_ls)
	#以下描画例。曜日や月、年などの各属性ごとに描画できる
	if group == "youbi":
		ratio_ls_weekday = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] <= 4]
		col_ratio = 0.5
		ax.scatter(ratio_ls_weekday, marker='s', color=cmap(col_ratio),label="weekday")
		ratio_ls_weekend = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] >= 5]
		col_ratio = 0.1
		ax.scatter(ratio_ls_weekend, marker='o', color=cmap(col_ratio),label="weekend")
		#print(np.mean(ratio_ls_weekend,axis=0))
		#print(np.mean(ratio_ls_weekday,axis=0))
	if group == "month":
		ratio_ls_firsthalf = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] <= 6]
		col_ratio = 0.8
		ax.scatter(ratio_ls_firsthalf, marker='s', color=cmap(col_ratio),label="firsthalf")
		ratio_ls_latterhalf = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] >= 7]
		col_ratio = 0.3
		ax.scatter(ratio_ls_latterhalf, marker='o', color=cmap(col_ratio),label="latterhalf")
	if group == "year":
		ratio_ls_2017 = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] == 2017]
		col_ratio = 0.2
		ax.scatter(ratio_ls_2017, marker='s', color=cmap(col_ratio),label="2017")
		ratio_ls_2018 = [one_ratio for ind, one_ratio in enumerate(ratio_ls) if label_ls[ind] == 2018]
		col_ratio = 0.7
		ax.scatter(ratio_ls_2018, marker='o', color=cmap(col_ratio),label="2018")
	#グラフの見た目の設定
	ax.clear_matplotlib_ticks()
	ax.ticks(axis='lbr', multiple=10, linewidth=1)
	fontsize = 10
	ax.set_title("Group: %s"%group, fontsize=fontsize)
	ax.left_axis_label("Quadrant 3", fontsize=fontsize)
	ax.right_axis_label("Quadrant 2", fontsize=fontsize)
	ax.bottom_axis_label("Quadrant 1", fontsize=fontsize)
	ax.legend()
	if saveFlag:
		figname = "graph_output/Ternary_"+group+".png"
		plt.savefig(figname)
	plt.show()


#特定のプロジェクト群に使った時間を日ごとにグラフ化 [toggl_visualize_util]
def drawTimeForParticularProjects(database,
								  project_dict_ls,
								  since_str,
								  until_str,
								  dict_labels=None,
								  saveFlag=False):
	#棒グラフの棒の高さの計算
	hours_ls_ls = []
	for one_project_dict in project_dict_ls:
		#特定のタスクに使っている時間を計算 [analyzer.py]
		one_hours_ls = countTimeForParticularTasks(database,
												   task_dict=one_project_dict,
												   since_str=since_str,
												   until_str=until_str)
		hours_ls_ls.append(one_hours_ls)
	#x軸に入れるものの作成
	dt_0 = str2Datetime(since_str+"T00:00:00+")
	dt_ls = [dt_0+datetime.timedelta(days = delta_day) for delta_day in range(len(one_hours_ls))]
	#描画部
	ax = plt.subplot()
	total_hours_ls = [0] * len(one_hours_ls) #グラフを積み上げるため、時間の和を計算する
	plt_ls = []
	for dict_ind in range(len(project_dict_ls)):
		#print(dict_ind)
		p = plt.bar(dt_ls,hours_ls_ls[dict_ind],bottom=total_hours_ls,width=0.7,alpha=0.8)
		plt_ls.append(p)
		total_hours_ls = [total_hours_ls[j]+hours_ls_ls[dict_ind][j] for j in range(len(total_hours_ls))]

	drawWeekendBand(dt_ls,ax) #土日を表す帯を描画 [toggl_visualize_util]
	if dict_labels is not None: #ラベルを描画
		plt.legend(plt_ls,dict_labels)
	plt.ylim([0,24])
	plt.xlabel("Date")
	plt.ylabel("Hours")
	if saveFlag:
		figname = "graph_output/Barplot_"+since_str+"_"+until_str+".png"
		plt.savefig(figname)
	plt.show()

#土日を表す帯を描画 [toggl_visualize_util]
def drawWeekendBand(dt_ls,ax):
	print("土日を表す帯を描画します")
	defineXaxisFormat(ax,interval=7) #x軸の表示方法定義 [toggl_visualize_util]
	for one_day in dt_ls:
		weekday_ind = one_day.weekday()
		#土曜日の帯を描画
		if weekday_ind == 5:
			left_edge  = one_day-datetime.timedelta(days = 0.5)
			right_edge = one_day+datetime.timedelta(days = 0.5)
			ax.fill_between([left_edge, right_edge], 0, 30, facecolor="#afafff", interpolate=True, alpha=0.3)
		#日曜日の帯を描画
		if weekday_ind == 6:
			left_edge  = one_day-datetime.timedelta(days = 0.5)
			right_edge = one_day+datetime.timedelta(days = 0.5)
			ax.fill_between([left_edge, right_edge], 0, 30, facecolor="#ffafaf", interpolate=True, alpha=0.3)

#x軸の表示方法定義 [toggl_visualize_util]
def defineXaxisFormat(ax,interval=7):
	#目盛り間隔の定義
	#days = mdates.AutoDateLocator()
	days = mdates.DayLocator(interval=interval)
	ax.xaxis.set_major_locator(days)
	#日付表現の定義
	daysFmt = mdates.DateFormatter("%b/%d")
	ax.xaxis.set_major_formatter(daysFmt)
