class QQFriends():
    def __init__(self):
        self.f = {}  # friends list
        self.g = {}  # group list
        self.d = {}  # discus group list
        self.r = {}  # recent list
        self.c = []
        self.group_info = {}
        self.user_info = {}

    def parse_friends(self, j):
        j = j['result']
        # category,  uin & flag
        for e in j['friends']:
            self.f[e['uin']] = {}
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
        j = j['result']
        self.r[0] = []
        self.r[1] = []
        for b in j:
            self.r[b['type']].append(b['uin'])

    def parse_online_buddies(self, j):
        pass

    def get_group_info(self, gid):
        return self.group_info.get(gid)

    def parse_group_info(self, j):
        j = j['result']['group_info']
        g = j['gid']
        del(j['gid'])
        self.group_info[g] = j
        return j

    def get_user_info(self, uin):
        return self.user_info.get(uin)

    def parse_user_info(self, j):
        j = j['result']
        u = j['uin']
        del(j['uin'])
        self.user_info[u] = j
        return j
