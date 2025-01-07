from Builder import *
import os
pro = project('ee')
main = page()
main.head = elements.head()
main.body = elements.body([elements.p(0,'GG')])
main.head
pro.addPage(main)
os.chdir('..')
pro.save()
g = pro.getPage('main.html')
print(g)