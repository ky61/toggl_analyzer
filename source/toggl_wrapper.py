
#Togglのラッパー [toggl_wrapper.py]

import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import sys
from .date_conv import str2Date

#Togglのラッパー [toggl_wrapper.py]
class TogglWrapper:
	def __init__(self, setting):
		self._api_token = setting["api_token"]
		self._user_agent = setting["user_agent"]
		#workspace_idの取得。1度取得してjsonに書き込めば、この手順は省ける
		r = requests.get('https://www.toggl.com/api/v8/workspaces',
			auth=(self._api_token, 'api_token'))
		workspace_id = r.json()[0]["id"]
		self._workspace_id = workspace_id
		self.setParams()
	#データ要求のパラメータセット
	def setParams(self,since='2017-06-01',until='2017-06-01'):
		self._params = {
			'user_agent': self._user_agent,		#登録しているメールアドレス(入力)
			'workspace_id': self._workspace_id,	#TogglのworkspaceIDを入力(入力)
			'since': since,			# データ取得開始日(入力)
			'until': until,			# データ取得終了日(入力)
		}
	#setparamsのパラメータに従ってデータ要求
	def requestToggl(self):
		r = requests.get('https://toggl.com/reports/api/v2/details',
			auth=HTTPBasicAuth(self._api_token, 'api_token'),
			params=self._params)
		data = r.json()["data"]
		return data

	#指定した数日間のタスクの生データをとってくる
	def fetchPeriodData(self, since="2017-04-01", until="2017-04-30"):
		date_s = str2Date(since)
		date_u = str2Date(until)
		raw_data_ls = []
		while date_s <= date_u:
			date_s_str = date_s.strftime('%Y-%m-%d')
			print(date_s_str + "のデータを抽出中です...",end="")
			self.setParams(date_s_str, date_s_str)
			daily_raw_data = self.requestToggl()
			#時系列順になるように反転する
			daily_raw_data.reverse()
			print("タスク数は%dです"%len(daily_raw_data))
			raw_data_ls += daily_raw_data
			date_s += datetime.timedelta(days = 1)
		return raw_data_ls
