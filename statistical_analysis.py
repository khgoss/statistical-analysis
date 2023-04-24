'''
Copyright (C)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext. 
For license issues, please contact:
Dr. Bing Ye
Life Sciences Institute
University of Michigan
210 Washtenaw Avenue, Room 5403
Ann Arbor, MI 48109-2216
USA
Email: bingye@umich.edu
'''

import scipy.stats as stats
import scikit_posthocs as sp
import statsmodels.stats.proportion as sm
import pandas as pd
import os
import openpyxl
from collections import OrderedDict

class data_mining():
	def __init__(self, data_in, control_in = None, paired_in = False, printAll_in = True, result_path_in = None):
		self.data = data_in
		self.control = control_in
		self.paired = paired_in
		self.printAll = printAll_in
		self.writer = pd.ExcelWriter(os.path.join(result_path_in,'data_mining_results.xlsx'))

	def normal(self, dataset):
		for i in dataset:
			if stats.shapiro(i).pvalue < 0.05:
				return False
		return True

	def two_groups(self):
		for behavior in self.data[0]:
			print(behavior)
			parameters = []
			pvalues = []
			statistics = []
			for parameter in self.data[0][behavior]:
				setA = self.data[0][behavior][parameter].dropna()
				setB = self.data[1][behavior][parameter].dropna()
				dataset = [setA, setB]
				if (self.normal(dataset)):
					if self.paired:
						test = "paired t-test"
						result = stats.ttest_rel(setA, setB)
					else:
						test = "unpaired t-test"
						result = stats.ttest_ind(setA, setB)
				else:
					if self.paired:
						test = "Wilcoxon test"
						result = stats.wilcoxon(setA, setB)
					else:
						test = "Mann Whitney U test"
						result = stats.mannwhitneyu(setA, setB)
				if (self.printAll == True or result.pvalue <= 0.05):
					print('\t', parameter)
					print('\t', "performing", test)
					print('\t'*2, "p-value: ", result.pvalue)
					print('\t'*2, "statistic: ", result.statistic)
					parameters.append(parameter)
					pvalues.append(result.pvalue)
					statistics.append(result.statistic)
			results = pd.DataFrame({"p-value":pvalues, "statistic":statistics}, index = parameters)
			results.to_excel(self.writer, sheet_name = behavior)

	def multiple_groups(self):
		for behavior in self.data[0]:
			print(behavior)
			parameters = []
			pvalues = []
			statistics = []
			for parameter in self.data[0][behavior]:
				dataset = []
				for i in range(len(self.data)):
					currentSet = self.data[i][behavior][parameter].dropna()
					dataset.append(currentSet)
				if self.control != None:
					currentSet = self.control[behavior][parameter].dropna()
					dataset.insert(0, currentSet)
				if self.normal(dataset):
					test = "ANOVA"
					result = stats.f_oneway(*dataset)
				else:
					if self.paired:
						test = "Friedman"
						result = stats.friedmanchisquare(*dataset)
					else:
						test = "Kruskal Wallis"
						result = stats.kruskal(*dataset)
				if self.printAll == True or result.pvalue <= 0.05:
					print('\t', parameter)
					print('\t', "performing", test)
					print('\t'*2, "p-value: ", result.pvalue)
					print('\t'*2, "statistic: ", result.statistic)
					parameters.append(parameter)
					pvalues.append(result.pvalue)
					statistics.append(result.statistic)
					if test == "ANOVA":
						if self.control==None:
							tukey = stats.tukey_hsd(*dataset)
							print(tukey)
						else:
							dunnett = stats.dunnett(dataset, self.control)
							print('\t'*2, "Dunnett's post-hoc results:")
							print("\t"*2+dunnett.to_string().replace("\n","\n\t\t"))
					else:
						dunn = sp.posthoc_dunn(dataset) 
						print('\t'*2, "Dunn's post-hoc results:")
						print("\t"*2+dunn.to_string().replace("\n","\n\t\t"))
			results = pd.DataFrame({"p-value":pvalues, "statistic":statistics}, index = parameters)
			results.to_excel(self.writer, sheet_name = behavior)

	def statistical_analysis(self):
		if len(self.data)==2 and self.control==None: #tests for two groups only
			self.two_groups()
		else: #tests for 3+ groups
			self.multiple_groups()
		self.writer.save()