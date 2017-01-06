try:
    import Tkinter as tk
    import ttk
    from ConfigParser import ConfigParser
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    from configparser import ConfigParser

from collections import namedtuple
import time


_font_name = 'Consolas'

def GameConfigParser():
    game_defaults = {
        'half_play_duration': '600',
        'half_time_duration': '300',
        'game_over_duration': '300'
    }
    parser = ConfigParser(defaults=game_defaults)
    parser.add_section('game')
    return parser

def sized_frame(master, height, width):
    F = tk.Frame(master, height=height, width=width)
    F.pack_propagate(0)  # Don't shrink
    return F


def SizedLabel(root, var, bg, fg, font, height, width):
    sf = sized_frame(root, height, width)
    l = tk.Label(sf, textvariable=var, bg=bg, fg=fg, font=font)
    l.pack(fill=tk.BOTH, expand=1)
    return sf


def SizedButton(root, callback, text, style, height, width):
    sf = sized_frame(root, height, width)
    b = ttk.Button(sf, text=text, command=callback, style=style)
    b.pack(fill=tk.BOTH, expand=1)
    return sf

def ManualEditScore(master, tb_offset, score, on_submit):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(400, 420, 200, 50 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    score_var = tk.IntVar(value=score)

    label_font = (_font_name, 96)

    def up():
        score_var.set(score_var.get() + 1)

    def dn():
        score_var.set(score_var.get() - 1)

    def cancel_clicked():
        root.destroy()

    def submit_clicked():
        root.destroy()
        on_submit(score_var.get())

    cancel_button = SizedButton(root, cancel_clicked, "CANCEL", "Red.TButton", 130, 400)
    cancel_button.grid(row=3, column=0, columnspan=2)

    submit_button = SizedButton(root, submit_clicked, "SUBMIT", "Green.TButton", 130, 400)
    submit_button.grid(row=2, column=0, columnspan=2)

    label = SizedLabel(root, score_var, "black", "white", label_font, 160, 300)
    label.grid(row=0, rowspan=2, column=0)

    up_button = SizedButton(root, up, "+", "Blue.TButton", 80, 100)
    up_button.grid(row=0, column=1)

    dn_button = SizedButton(root, dn, "-", "Grey.TButton", 80, 100)
    dn_button.grid(row=1, column=1)


def ConfirmRefTimeOut(master, tb_offset, on_edit, on_resume):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 190, 0, 115 + 170 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    def resume_clicked():
        root.destroy()
        on_resume()

    resume_button = SizedButton(root, resume_clicked, "RESUME\nPLAY", "Big.Green.TButton", 190, 400)
    resume_button.grid(row=0, column=0)

    edit_button = SizedButton(root, on_edit, "EDIT TIME", "Big.Orange.TButton", 190, 400)
    edit_button.grid(row=0, column=1)


def ManualEditTime(master, tb_offset, clock_at_pause, on_cancel, on_submit):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 310, 0, 170 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    clock_at_pause_var = tk.IntVar(value=clock_at_pause)

    label_font = (_font_name, 96)
    playpause_button_font = (_font_name, 36)
    game_clock_font = (_font_name, 72)

    def game_clock_s_up():
        clock_at_pause_var.set(clock_at_pause_var.get() + 1)

    def game_clock_s_dn():
        clock_at_pause_var.set(clock_at_pause_var.get() - 1)

    def game_clock_m_up():
        clock_at_pause_var.set(clock_at_pause_var.get() + 60)

    def game_clock_m_dn():
        clock_at_pause_var.set(clock_at_pause_var.get() - 60)

    def cancel_clicked():
        root.destroy()
        on_cancel()

    def submit_clicked():
        root.destroy()
        on_submit(clock_at_pause_var.get())

    cancel_button = SizedButton(root, cancel_clicked, "CANCEL", "Red.TButton", 150, 400)
    cancel_button.grid(row=2, column=0, columnspan=2)

    submit_button = SizedButton(root, submit_clicked, "SUBMIT", "Green.TButton", 150, 400)
    submit_button.grid(row=2, column=2, columnspan=2)

    m_up_button = SizedButton(root, game_clock_m_up, u"Min \u2191", "Blue.TButton", 80, 200)
    m_up_button.grid(row=0, column=0)

    m_dn_button = SizedButton(root, game_clock_m_dn, u"Min \u2193", "Grey.TButton", 80, 200)
    m_dn_button.grid(row=1, column=0)

    s_up_button = SizedButton(root, game_clock_s_up, u"Sec \u2191", "Blue.TButton", 80, 200)
    s_up_button.grid(row=0, column=3)

    s_dn_button = SizedButton(root, game_clock_s_dn, u"Sec \u2193", "Grey.TButton", 80, 200)
    s_dn_button.grid(row=1, column=3)

    game_clock_var = tk.StringVar()

    def on_clock_changed(*args):
        x = clock_at_pause_var.get()
        game_clock_var.set('%d:%02d' % (x // 60, x % 60))
    on_clock_changed()

    clock_at_pause_var.trace('w', on_clock_changed)

    game_clock_new = SizedLabel(root, game_clock_var, "black", "blue", game_clock_font,
                                160, 400)
    game_clock_new.grid(row=0, rowspan=2, column=1, columnspan=2)


def ScoreColumn(root, column, team_color, score_color, refresh_ms, get_score,
        score_changed):
    score_font = (_font_name, 96)
    score_height = 120
    score_width = 200

    label_font = (_font_name, 36)
    label_height = 50
    label_width = score_width

    button_height = 120
    button_width = score_width

    penalty_height = 190
    penalty_width = score_width

    score_var = tk.IntVar()
    score_label = SizedLabel(root, score_var, "black",
                             score_color, score_font, score_height,
                             score_width)
    score_label.grid(row=0, column=column)

    def refresh_score():
        score_var.set(get_score())
        score_label.after(refresh_ms, lambda: refresh_score())
    score_label.after(refresh_ms, lambda: refresh_score())

    label_var = tk.StringVar(value=team_color.upper())
    label = SizedLabel(root, label_var, score_color, "black",
                       label_font, label_height, label_width)
    label.grid(row=1, column=column)

    button = SizedButton(root, score_changed,
                         team_color.upper() + "\nSCORE", "Cyan.TButton",
                         button_height, button_width)
    button.grid(row=2, column=column)

    penalty = tk.Frame(root, height=penalty_height, width=penalty_width,
                       bg="black")
    penalty.grid(row=3, column=column)

    return root

def create_button_style(name, background, sz):
    style = ttk.Style()
    style.configure(name, foreground='black', background=background,
        relief='flat', font=(_font_name, sz))
    style.map(name, background=[('active', background)])


def create_styles():
    big_font_size = 36
    create_button_style('Big.Green.TButton', 'green', big_font_size)
    create_button_style('Big.Orange.TButton', 'orange', big_font_size)

    font_size = 36
    create_button_style('Cyan.TButton', 'dark cyan', font_size)
    create_button_style('Green.TButton', 'green', font_size)
    create_button_style('Grey.TButton', 'grey', font_size)
    create_button_style('Blue.TButton', 'light blue', font_size)
    create_button_style('Red.TButton', 'red', font_size)
    create_button_style('Yellow.TButton', 'yellow', font_size)


class NormalView(object):

    def __init__(self, mgr, iomgr, NO_TITLE_BAR, cfg=None):
        self.mgr = mgr
        self.iomgr = iomgr
        self.cfg = cfg or GameConfigParser()

        self.root = tk.Tk()
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(800, 480, 0, 0))
        if NO_TITLE_BAR:
            self.root.overrideredirect(1)
            self.tb_offset = 0
        else:
            self.tb_offset = 70

        refresh_ms = 50

        create_styles()
        ScoreColumn(self.root, 0, 'white', 'white',
                    refresh_ms, lambda: self.mgr.whiteScore(),
                    lambda: self.edit_white_score())

        self.center_column(refresh_ms)
        ScoreColumn(self.root, 2, 'black', 'blue',
                    refresh_ms, lambda: self.mgr.blackScore(),
                    lambda: self.edit_black_score())

        def poll_clicker(self):
            if self.iomgr.readClicker():
                print("remote clicked")
                self.gong_clicked()
            else:
                self.iomgr.setSound(0)
            self.root.after(refresh_ms, lambda: poll_clicker(self))
        self.root.after(refresh_ms, lambda: poll_clicker(self))

    def center_column(self, refresh_ms):
        clock_font = (_font_name, 96)
        clock_height = 120
        clock_width = 400

        status_font = (_font_name, 36)
        status_height = 50
        status_width = clock_width

        gong_height = 120
        gong_width = clock_width

        ref_signal_height = 190
        ref_signal_width = clock_width

        time_change_height = ref_signal_height
        time_change_width = clock_width

        self.status_var = tk.StringVar()
        self.status_var.set("FIRST HALF")

        self.game_clock_var = tk.StringVar()
        self.game_clock_var.set("##:##")
        self.game_clock_label = SizedLabel(self.root, self.game_clock_var, "black", "#000fff000",
                                           clock_font, clock_height, clock_width)
        self.game_clock_label.grid(row=0, column=1)

        status_label = SizedLabel(self.root, self.status_var, "black", "#000fff000", status_font,
                                  status_height, status_width)
        status_label.grid(row=1, column=1)

        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

        gong_button = SizedButton(self.root, lambda: self.gong_clicked(), "GONG",
                                  "Red.TButton", gong_height,
                                  gong_width)
        gong_button.grid(row=2, column=1)

        time_button = SizedButton(self.root, lambda: self.ref_timeout_clicked(),
                                  "REF TIMEOUT", "Yellow.TButton",
                                  time_change_height, time_change_width)
        time_button.grid(row=3, column=1)

        # ref_signal_cover = tk.Frame(self.root, height=ref_signal_height,
        #                         width=ref_signal_width, bg="black")
        #ref_signal_cover.grid(row=3, column=1)

    def refresh_time(self):
        game_clock = self.mgr.gameClock()
        game_mins = game_clock // 60
        game_secs = game_clock % 60
        self.game_clock_var.set("%02d:%02d" % (game_mins, game_secs))

        if game_clock <= 0:
            if self.mgr.gameStateFirstHalf():
                self.mgr.setGameStateHalfTime()
                self.mgr.setGameClock(self.cfg.getint('game', 'half_time_duration'))
                self.gong_clicked()
            elif self.mgr.gameStateHalfTime():
                self.mgr.setGameStateSecondHalf()
                self.mgr.setGameClock(self.cfg.getint('game', 'half_play_duration'))
                self.gong_clicked()
            elif self.mgr.gameStateSecondHalf():
                self.mgr.setGameStateGameOver()
                self.mgr.setGameClock(self.cfg.getint('game', 'game_over_duration'))
                self.gong_clicked()
            elif self.mgr.gameStateGameOver():
                self.mgr.setBlackScore(0)
                self.mgr.setWhiteScore(0)
                self.mgr.setGameStateFirstHalf()
                self.mgr.setGameClock(self.cfg.getint('game', 'half_play_duration'))
                if self.mgr.gameClockRunning():
                    self.gong_clicked()

        if self.mgr.timeoutStateRef():
            self.status_var.set("REF TIMEOUT")
        elif self.mgr.timeoutStateWhite():
            self.status_var.set("WHT TIMEOUT")
        elif self.mgr.timeoutStateBlack():
            self.status_var.set("BLK TIMEOUT")
        elif self.mgr.gameStateFirstHalf():
            self.status_var.set("FIRST HALF")
        elif self.mgr.gameStateHalfTime():
            self.status_var.set("HALF TIME")
        elif self.mgr.gameStateSecondHalf():
            self.status_var.set("SECOND HALF")
        elif self.mgr.gameStateGameOver():
            self.status_var.set("GAME OVER")

        refresh_ms = 50
        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

    def gong_clicked(self):
        print("gong clicked")
        self.mgr.setGameClockRunning(True)
        self.iomgr.setSound(1)
        time.sleep(1)
        self.iomgr.setSound(0)

    def edit_white_score(self):
        ManualEditScore(self.root, self.tb_offset, self.mgr.whiteScore(),
                        lambda x: self.mgr.setWhiteScore(x))

    def edit_black_score(self):
        ManualEditScore(self.root, self.tb_offset, self.mgr.blackScore(),
                        lambda x: self.mgr.setBlackScore(x))

    def edit_time(self, clock_at_pause):
        def submit_clicked(game_clock):
            self.mgr.setGameClock(max(game_clock, 0))
            self.set_paused_time()

        ManualEditTime(self.root, self.tb_offset, clock_at_pause,
                lambda: None, submit_clicked)

    def set_paused_time(self):
        # The awkward sequence here is to work around a bug in the c++ code,
        # which can't easily be fixed at the moment: it is baked into the displays.
        #
        # The bug itself is that self.mgr.gameClock() returns the wrong value
        # when it is called while the clock is paused. It does produce the correct
        # value when the clock is running, so we save it off, stop the clock, and
        # write the saved value so that all of the clock displays get the correct
        # paused time.
        clock_at_pause = self.mgr.gameClock()
        self.mgr.setGameClockRunning(False)
        self.mgr.setGameClock(max(clock_at_pause, 0))
        self.refresh_time()

    def ref_timeout_clicked(self):
        running_at_pause = self.mgr.gameClockRunning()
        self.state_before_pause = self.mgr.gameState()
        self.mgr.setTimeoutStateRef()
        self.set_paused_time()

        def resume():
            self.mgr.setGameState(self.state_before_pause)
            self.mgr.setTimeoutStateNone()
            self.mgr.setGameClockRunning(running_at_pause)

        ConfirmRefTimeOut(self.root,
                          self.tb_offset,
                          lambda: self.edit_time(self.mgr.gameClock()),
                          resume)
