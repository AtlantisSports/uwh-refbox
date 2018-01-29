from . import ui
from uwh.gamemanager import GameManager, TeamColor
from .noiomanager import IOManager

def test_refbox_config_parser():
    cfg = ui.RefboxConfigParser()
    assert type(cfg.getint('game', 'half_play_duration')) == int
    assert type(cfg.getint('game', 'half_time_duration')) == int


def test_sized_frame():
    assert ui.sized_frame(None, 1, 2)


def test_score_column():
    root = ui.sized_frame(None, 1, 2)
    assert ui.ScoreColumn(root, 2, 'black', 'blue', 5, lambda: 42, lambda: 43,
                          lambda: 44, ui.RefboxConfigParser())


def test_normal_view():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    assert nv.mgr.gameClockRunning() is False
    assert nv.mgr.gameClock() > 0

    nv.gong_clicked()
    assert nv.mgr.gameClockRunning() is True


def test_game_over():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameStateSecondHalf()
    nv.mgr.setGameClock(0)
    nv.mgr.setGameClockRunning(True)

    nv.refresh_time()
    assert nv.mgr.gameStateGameOver() is True
    assert nv.mgr.gameClockRunning() is False


def test_edit_score():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.edit_white_score()
    nv.edit_black_score()


def test_inc_score():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.increment_white_score()
    nv.increment_black_score()


def test_edit_time():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameClock(2)
    nv.edit_time()
    assert nv.mgr.gameClock() == 2


def test_PlayerSelectNumpad():
    root = ui.sized_frame(None, 1, 2)
    psn = ui.PlayerSelectNumpad(root, '')

    assert psn.get_value() == ''

    psn.clicked('1')
    psn.clicked('3')
    assert psn.get_value() == '13'

    psn.clicked('del')
    assert psn.get_value() == '1'

    psn.clicked('del')
    assert psn.get_value() == ''

    psn.clicked('del')
    assert psn.get_value() == ''

    psn.clicked('4')
    psn.clicked('2')
    assert psn.get_value() == '42'

def test_add_penalty():
    nv = ui.NormalView(GameManager(), IOManager(), NO_TITLE_BAR=True)
    nv.mgr.setGameClock(2)
    nv.add_penalty(TeamColor.black)
