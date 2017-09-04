from .uwhscores import Tournament, Game, Teams, Team, Database

def test_Tournament():
    data = {
      "tournament": {
        "divisions": [
          "E",
          "O"
        ],
        "end_date": "2015-02-08T00:00:00",
        "is_active": 0,
        "location": "Browndeer, WI",
        "name": "2015 CanAm Midwestern Championships",
        "pools": [
          "1",
          "2"
        ],
        "short_name": "cmcs2015",
        "start_date": "2015-02-06T00:00:00",
        "tid": 4
      }
    }

    schema = Tournament()
    t = schema.deserialize(data['tournament'])

    assert t['tid'] == 4
    assert t['is_active'] == 0
    assert t['name'] == "2015 CanAm Midwestern Championships"


def test_game():
    data = {
      "black": "Rogue Ten",
      "black_id": 1,
      "day": "Sat",
      "forfeit": None,
      "gid": 1,
      "note_b": "",
      "note_w": "",
      "pool": "1",
      "score_b": 3,
      "score_w": 3,
      "start_time": "2017-01-28T09:00:00",
      "tid": 10,
      "white": "Colorado Aquatic Sloths",
      "white_id": 2
    }

    schema = Game()
    g = schema.deserialize(data)

    assert g['gid'] == 1
    assert g['black'] == "Rogue Ten"
    assert g['white'] == "Colorado Aquatic Sloths"


def test_teams():
    data = {
      "teams": [
        {
          "division": "O",
          "name": "Colorado Aquatic Sloths",
          "team_id": 2
        },
        {
          "division": "O",
          "name": "Colorado Lighting Strikers",
          "team_id": 7
        },
        {
          "division": "O",
          "name": "Dallas",
          "team_id": 4
        },
      ]
    }

    schema = Teams()
    ts = schema.deserialize(data['teams'])

    assert ts[0]['name'] == "Colorado Aquatic Sloths"
    assert ts[2]['name'] == "Dallas"


def test_database():
    db = Database()

    tid = 10
    gid = 4
    assert db.get_tournament(tid) != ""
    assert db.get_games(tid) != ""
    assert db.get_games(tid) != ""
    assert db.get_game(tid, gid) != ""
    assert db.get_teams(tid) != ""
