import tkinter as tk
from . import ui
from uwh.gamemanager import GameManager, TeamColor, Penalty
from .noiomanager import IOManager

import itertools

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

def test_PenaltyEditor_submit():
    def on_submit(self, player, duration):
       assert player == '42'
       assert duration == 5 * 60
       self.submit_was_clicked = True

    def on_delete(self):
       self.delete_was_clicked = True

    mgr = GameManager()
    cfg = ui.RefboxConfigParser()
    root = tk.Tk()
    editor = ui.PenaltyEditor(root, 0, mgr, cfg, TeamColor.black, on_delete, on_submit, None)
    editor.submit_was_clicked = False
    editor.delete_was_clicked = False

    editor._numpad.clicked('4')
    editor._numpad.clicked('2')

    editor.time_select(5 * 60)

    editor.submit_clicked()
    assert editor.submit_was_clicked == True
    assert editor.delete_was_clicked == False


def test_PenaltyEditor_delete():
    penalty = Penalty(37, TeamColor.black, 3 * 60)

    def on_submit(self, player, duration):
       self.submit_was_clicked = True

    def on_delete(self, penalty):
       assert penalty.duration() == 3 * 60
       assert penalty.player() == 37
       self.delete_was_clicked = True

    mgr = GameManager()
    cfg = ui.RefboxConfigParser()
    root = tk.Tk()
    editor = ui.PenaltyEditor(root, 0, mgr, cfg, TeamColor.black, on_delete, on_submit, penalty)
    editor.submit_was_clicked = False
    editor.delete_was_clicked = False

    editor._numpad.clicked('4')
    editor._numpad.clicked('2')

    editor.time_select(5 * 60)

    editor.delete_clicked()
    assert editor.submit_was_clicked == False
    assert editor.delete_was_clicked == True

def test_TimeEditor():
    def on_submit(new_time):
        assert new_time == 59
        editor.submit_was_clicked = True

    def on_cancel():
        editor.cancel_was_clicked = True

    cfg = ui.RefboxConfigParser()
    root = tk.Tk()

    editor = ui.TimeEditor(root, 0, 5 * 60 + 2, on_submit,
                           on_cancel, cfg)
    editor.submit_was_clicked = False
    editor.cancel_was_clicked = False

    editor.game_clock_m_dn()
    assert editor.clock_at_pause_var.get() == 4 * 60 + 2

    editor.game_clock_s_dn()
    assert editor.clock_at_pause_var.get() == 4 * 60 + 1

    editor.game_clock_m_dn()
    assert editor.clock_at_pause_var.get() == 3 * 60 + 1

    editor.game_clock_s_dn()
    assert editor.clock_at_pause_var.get() == 3 * 60 + 0

    editor.game_clock_s_dn()
    assert editor.clock_at_pause_var.get() == 2 * 60 + 59

    editor.game_clock_m_dn()
    assert editor.clock_at_pause_var.get() == 1 * 60 + 59

    editor.game_clock_m_dn()
    assert editor.clock_at_pause_var.get() == 59

    editor.game_clock_m_dn()
    assert editor.clock_at_pause_var.get() == 0

    editor.game_clock_s_dn()
    assert editor.clock_at_pause_var.get() == 0

    editor.game_clock_m_up()
    assert editor.clock_at_pause_var.get() == 60

    editor.game_clock_s_up()
    assert editor.clock_at_pause_var.get() == 61

    editor.game_clock_s_dn()
    editor.game_clock_s_dn()
    assert editor.clock_at_pause_var.get() == 59

    editor.submit_clicked()
    assert editor.submit_was_clicked == True
    assert editor.cancel_was_clicked == False

    editor = ui.TimeEditor(root, 0, 5 * 60 + 2, on_submit,
                           on_cancel, cfg)
    editor.submit_was_clicked = False
    editor.cancel_was_clicked = False

    editor.cancel_clicked()
    assert editor.submit_was_clicked == False
    assert editor.cancel_was_clicked == True


def test_ScoreEditor():
    def on_submit(new_score):
        assert new_score == 99
        editor.submit_was_clicked = True

    cfg = ui.RefboxConfigParser()
    root = tk.Tk()
    editor = ui.ScoreEditor(root, 0, 1, True, on_submit, cfg)
    editor.submit_was_clicked = False

    editor.dn()
    editor.dn()
    editor.dn()
    assert editor.score_var.get() == 0

    editor.up()
    assert editor.score_var.get() == 1

    for _ in itertools.repeat(None, 110):
        editor.up()

    assert editor.score_var.get() == 99

    editor.submit_clicked()
    assert editor.submit_was_clicked == True

    editor = ui.ScoreEditor(root, 0, 42, True, on_submit, cfg)
    editor.submit_was_clicked = False

    editor.cancel_clicked()
    assert editor.submit_was_clicked == False
