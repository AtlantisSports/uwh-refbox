import ssl
import urllib.request
import json
import colander

class Divisions(colander.SequenceSchema):
    division = colander.SchemaNode(colander.String())

class Pools(colander.SequenceSchema):
    pool = colander.SchemaNode(colander.String())

class Tournament(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    short_name = colander.SchemaNode(colander.String())
    divisions = Divisions(missing=[])
    start_date = colander.SchemaNode(colander.DateTime())
    end_date = colander.SchemaNode(colander.DateTime())
    is_active = colander.SchemaNode(colander.Int())
    location = colander.SchemaNode(colander.String())
    pools = Pools(missing=[])
    tid = colander.SchemaNode(colander.Int())

class Game(colander.MappingSchema):
    black = colander.SchemaNode(colander.String())
    black_id = colander.SchemaNode(colander.Int())
    day = colander.SchemaNode(colander.String())
    forefit = colander.SchemaNode(colander.String(allow_empty=True))
    gid = colander.SchemaNode(colander.Int())
    note_b = colander.SchemaNode(colander.String())
    note_w = colander.SchemaNode(colander.String())
    start_time = colander.SchemaNode(colander.DateTime())
    tid = colander.SchemaNode(colander.Int())
    white = colander.SchemaNode(colander.String())
    white_id = colander.SchemaNode(colander.Int())

class Team(colander.MappingSchema):
    division = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String())
    team_id = colander.SchemaNode(colander.Int())

class Teams(colander.SequenceSchema):
    team = Team()

class Database(object):
    def __init__(self):
        self.ssl_context = ssl._create_unverified_context()
        self.api = "https://uwhscores.com/api/v1"

    def get(self, url):
        with urllib.request.urlopen(url, context=self.ssl_context) as request:
            return json.loads(request.read().decode())

    def get_tournament(self, tid):
        # https://uwhscores.com/api/v1/tournaments/$tid
        return self.get("%s/tournaments/%d" % (self.api, tid))

    def get_games(self, tid):
        return self.get("%s/tournaments/%d/games" % (self.api, tid))

    def get_game(self, tid, gid):
        # https://uwhscores.com/api/v1/tournaments/$tid/games/$gid
        return self.get("%s/tournaments/%d/games/%d" % (self.api, tid, gid))

    def get_teams(self, tid):
        # https://uwhscores.com/api/v1/tournaments/$tid/teams
        return self.get("%s/tournaments/%d/teams" % (self.api, tid))

