import pandas as pd
import matplotlib.pyplot as plt

# df = pd.read_csv('data.csv')
df = pd.read_csv('outlier_removed.csv')
# df = df[:100]
fig, axes = plt.subplots(nrows=3, ncols=2, sharex=True, sharey=True)
plt.subplots_adjust(wspace=0.2, hspace=0.5)
plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])

gs = fig.add_gridspec(3, 2)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[2, :])
df[df['year'] == 2016].plot.scatter('id', 'units_sold', c='red', ax=ax1)
ax1.title.set_text('Year 2016')
df[df['year'] == 2017].plot.scatter('id', 'units_sold', c='green', ax=ax2)
ax2.title.set_text('Year 2017')
df[df['year'] == 2018].plot.scatter('id', 'units_sold', c='orange', ax=ax3)
ax3.title.set_text('Year 2018')
df[df['year'] == 2019].plot.scatter('id', 'units_sold', c='pink', ax=ax4)
ax4.title.set_text('Year 2019')
df[df['year'] == 2020].plot.scatter('id', 'units_sold', c='blue', ax=ax5)
ax5.title.set_text('Year 2020')

plt.show()
