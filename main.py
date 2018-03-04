
import sys
import datetime
import json
import pickle

from source.toggl_wrapper import TogglWrapper
from source.toggl_database_util import updateTogglDB, cut_database
#1日の中での時間の使い方の描画 [toggl_visualize_util]
from source.toggl_visualize_util import drawTimeline
#各領域にどれくらい使っているか三角グラフにより可視化 [toggl_visualize_util]
from source.toggl_visualize_util import drawQuadrant
#特定のプロジェクト群に使った時間を日ごとにグラフ化 [toggl_visualize_util]
from source.toggl_visualize_util import drawTimeForParticularProjects

with open("./data/setting.json","r") as j:
	setting = json.load(j)
tw = TogglWrapper(setting) #Togglのラッパー [toggl_wrapper.py]
filename = "./data/database.pickle"
database = updateTogglDB(filename,tw)

#以下、可視化の例
#特定のタスクに使っている時間を計算
project_dict_emergency = {
	"1. Research": 0,
	"1. Presentation": 0,
	"1. Work": 0,
	"3. Mail": 0,
}
project_dict_othercreative = {
	"2. DIY":0,
	"2. Training":0,
	"2. Output":0,
	"2. Health":0,
	"2. Input":0,
}
project_dict_ls = [project_dict_emergency, project_dict_othercreative]
#特定のプロジェクト群に使った時間を日ごとにグラフ化 [toggl_visualize_util]
drawTimeForParticularProjects(database,
							  project_dict_ls,
							  since_str="2018-01-01",
							  until_str="2018-02-28",
							  dict_labels=["Inevitable work","Other work"],
							  saveFlag=True)

#各領域にどれくらい使っているか三角グラフにより可視化 [toggl_visualize_util]
group = "youbi"  #"youbi","month","year"の中から選択
three_region_ls = ["第一領域", "第二領域", "第三領域"]
drawQuadrant(
			database=database,
			three_region_ls=three_region_ls,
			group=group,
			saveFlag=True
			)

#1日の中での時間の使い方の描画 [toggl_visualize_util]
drawTimeline(database, "2017-06-01", "2017-07-31",saveFlag=True)