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
        self.r[2] = []
        for b in j:
            self.r[b['type']].append(b['uin'])

    def parse_online_buddies(self, j):
        pass

    def get_group_info(self, gid):
        return self.group_info.get(gid)

    def parse_group_info(self, j):
        j = j['result']
        g = j['ginfo']
        g['members'] = {m['muin']: {} for m in g['members']} # ignore mflags
        for m in j['stats']:
            g['members'][m['uin']].update(m)
        for m in j['minfo']:
            g['members'][m['uin']].update(m)
        for m in j['cards']:
            g['members'][m['muin']].update(m)
        for m in j['vipinfo']:
            g['members'][m['u']]['vip_level'] = (
                m['is_vip'] and m['vip_level'])
        for m in g['members'].values():
            m.pop('uin', None)
            m.pop('muin', None)
            m.pop('u', None)
        self.group_info[g['gid']] = g
        return g

    def get_user_info(self, uin):
        return self.user_info.get(uin)

    def parse_user_info(self, j):
        self.user_info[j['result']['uin']] = j['result']
        return j['result']