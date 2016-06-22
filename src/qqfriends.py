class QQFriends():
    def __init__(self):
        self.f = dict()  # friends list
        self.g = dict()  # group list
        self.d = dict()  # discus group list
        self.r = dict()  # recent list
        self.c = []

    def parse_friends(self, j):
        j = j['result']
        # category,  uin & flag
        for e in j['friends']:
            self.f[e['uin']] = dict()
            self.f[e['uin']]['category'] = e['categories']
            self.f[e['uin']]['flag'] = e['flag']

        # marknames
        for e in j['marknames']:
            self.f[e['uin']]['markname'] = e['markname']
            #  self.f[e['uin']]['mType'] = e['type']

        # vipinfo
        for e in j['vipinfo']:
            self.f[e['u']]['vip'] = e['is_vip'] and e['vip_level']

        # user info
        for e in j['info']:
            self.f[e['uin']]['nickname'] = e['nick']
            self.f[e['uin']]['face'] = e['face']
            self.f[e['uin']]['flag'] = e['flag']

        # categories
        for e in j['categories']:
            self.c.append(e['name'])

    def parse_groups(self, j):
        j = j['result']
        self.g = {e['gid']: e for e in j['gnamelist']}
        for e in self.g.values():
            del(e['gid'])

    def parse_discus(self, j):
        j = j['result']
        self.d = {e['did']: e for e in j['dnamelist']}
        for e in self.d.values():
            del(e['did'])

    def parse_recent(self, j):
        self.r = j['result']
