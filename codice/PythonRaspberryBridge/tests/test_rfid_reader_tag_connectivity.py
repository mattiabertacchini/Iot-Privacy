#https://pypi.org/project/who-is-on-my-wifi/
#https://www.winpcap.org/install/

from who_is_on_my_wifi import *

WHO = who() # who(n)
for j in range(0, len(WHO)):
	comm = f"\n{WHO[j][0]} {WHO[j][1]}\n{WHO[j][2]} {WHO[j][3]}\n{WHO[j][4]} {WHO[j][5]}\n"
	print(comm)
