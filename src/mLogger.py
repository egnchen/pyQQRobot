import time

def output(*s,sep=' ',end='\n',file=None,flush=False):
	v('print',sep.join(map(lambda x:str(x),s)))

def w(tag,s):
	print('\033[43;30m%s\033[0m %s \033[4m%s\033[0;1m\t%s\033[0m' % 
		('WARN',time.strftime('%H:%M:%S'),tag,str(s)))

def i(tag,s):
	print('\033[42;30m%s\033[0m %s \033[4m%s\033[0;1m\t%s\033[0m' % 
		('INFO',time.strftime('%H:%M:%S'),tag,str(s)))

def e(tag,s):
	print('\033[41;37m%s\033[0m %s \033[4m%s\033[0;1m\t%s\033[0m' % 
		('ERRO',time.strftime('%H:%M:%S'),tag,str(s)))

def v(tag,s):
	print('\033[47;30m%s\033[0m %s \033[4m%s\033[0;1m\t%s\033[0m' % 
		('VERB',time.strftime('%H:%M:%S'),tag,str(s)))

if __name__=='__main__':
	w('tag','this is a warning')
	i('tag','this is an information')
	e('tag','this is an error')
	v('tag','this is a verbose man')
