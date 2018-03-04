
import datetime
import numpy as np
import matplotlib.pyplot as plt
#データベースの一部を取ってくる [toggl_database_util]
from .toggl_database_util import cut_database
from .date_conv import str2Date, yesterdaysStr

#特定のタスクに使っている時間を計算 [analyzer.py]
def countTimeForParticularTasks(database,task_dict,since_str,until_str):
	date_s = str2Date(since_str)
	date_u = str2Date(until_str)
	delta_days = (date_u - date_s).total_seconds()/60/60/24+1
	latestday = 0
	hours4tasks_ls = []
	#各日毎に計数
	for day in range(int(delta_days)):
		until_dt_tmp = date_s + datetime.timedelta(days = day)
		until_str_tmp = until_dt_tmp.strftime("%Y-%m-%d")
		if until_str_tmp == yesterdaysStr(): latestday=day+1 #グラフの縦線をうまく引くための処理
		#データベースの一部を取ってくる [toggl_database_util]
		sub_database = cut_database(database,since_str=until_str_tmp,until_str=until_str_tmp)
		for one_task in sub_database:
			project_name = one_task["project"]
			if project_name in task_dict: task_dict[project_name] += one_task["dur"]/1000/60/60
		hours4tasks_perday = 0
		for key in task_dict: hours4tasks_perday += task_dict[key]
		#print(hours4tasks_perday)
		hours4tasks_ls.append(hours4tasks_perday)
		for one_key in task_dict: task_dict[one_key] = 0
	return hours4tasks_ls