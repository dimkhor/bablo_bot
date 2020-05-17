def month_graph(vals,labels):
	import numpy as np
	import matplotlib.pyplot as plt

	fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(aspect="equal"))

	explode = tuple([0.025 for i in range(len(vals))])
	colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral','blue','red']
	def func(pct, allvals):
	    absolute = int(pct/100.*np.sum(allvals))
	    return "{:.1f}%\n{:d} р".format(pct, absolute)
	ax.pie(vals, autopct=lambda pct: func(pct, vals),explode=explode,wedgeprops={'edgecolor': 'black'},
	                                  colors=colors,textprops={'fontsize': 12},shadow=True)
	ax.legend(labels,loc='upper left', bbox_to_anchor=(0.9, 0.92),prop={'size':18},)
	plt.savefig(r'C:\Users\dmitriy.khoroshenkiy\Desktop\cs\bablo_bot\fig\curr_month.png', bbox_inches='tight')
	return(r'C:\Users\dmitriy.khoroshenkiy\Desktop\cs\bablo_bot\fig\curr_month.png')

def month_graph_by_day(dt,vals):
	import numpy as np
	import matplotlib.pyplot as plt

	ind = np.arange(len(vals))  # the x locations for the groups
	width = 0.35  # the width of the bars

	fig, ax =plt.subplots(figsize = [7,5])
	rects1 = ax.bar(ind, vals, width,color='SkyBlue')

	ax.set_xticks(ind)
	ax.set_xticklabels(tuple(dt))

	def autolabel(rects, xpos='center'):
	    xpos = xpos.lower()  # normalize the case of the parameter
	    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
	    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
	                '{}'.format(height), ha=ha[xpos], va='bottom')

	autolabel(rects1, "center")
	plt.savefig(r'C:\Users\dmitriy.khoroshenkiy\Desktop\cs\bablo_bot\fig\curr_month_by_day.png', bbox_inches='tight')
	return(r'C:\Users\dmitriy.khoroshenkiy\Desktop\cs\bablo_bot\fig\curr_month_by_day.png')
