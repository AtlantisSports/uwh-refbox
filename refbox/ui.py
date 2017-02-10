import tkinter as tk
from tkinter import ttk
from configparser import ConfigParser
import os
from .timeoutmanager import TimeoutManager

_font_name = 'Consolas'

def GameConfigParser():
    game_defaults = {
        'half_play_duration': '600',
        'half_time_duration': '180',
    }
    parser = ConfigParser(defaults=game_defaults)
    parser.add_section('game')
    return parser

def sized_frame(master, height, width):
    F = tk.Frame(master, height=height, width=width)
    F.pack_propagate(0)  # Don't shrink
    return F


def SizedLabel(root, text, bg, fg, font, height, width):
    sf = sized_frame(root, height, width)

    if isinstance(text, str):
        l = tk.Label(sf, text=text, bg=bg, fg=fg, font=font)
    else:
        l = tk.Label(sf, textvariable=text, bg=bg, fg=fg, font=font)

    l.pack(fill=tk.BOTH, expand=1)
    return sf


def SizedButton(root, callback, text, style, height, width):
    sf = sized_frame(root, height, width)

    if isinstance(text, str):
        b = ttk.Button(sf, text=text, command=callback, style=style)
    else:
        b = ttk.Button(sf, textvariable=text, command=callback, style=style)

    b.pack(fill=tk.BOTH, expand=1)
    return sf


def maybe_hide_cursor(root):
    # Don't show a cursor on Pi.
    if os.uname().machine == 'armv7l':
        root.configure(cursor='none')

def EditTime(master, tb_offset, clock_at_pause, on_submit):
    root = tk.Toplevel(master, background='black')
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 480, 0, tb_offset))

    maybe_hide_cursor(root)

    root.overrideredirect(1)
    root.transient(master)

    space = tk.Frame(root, height=50, width=100, bg="black")
    space.grid(row=0, column=0)

    clock_at_pause_var = tk.IntVar(value=clock_at_pause)

    game_clock_font = (_font_name, 72)

    def game_clock_s_up():
        x = clock_at_pause_var.get()
        clock_at_pause_var.set(x + 1)

    def game_clock_s_dn():
        x = clock_at_pause_var.get()
        if x > 0:
            clock_at_pause_var.set(x - 1)

    def game_clock_m_up():
        x = clock_at_pause_var.get()
        clock_at_pause_var.set(x + 60)

    def game_clock_m_dn():
        x = clock_at_pause_var.get()
        if x - 60 >= 0:
            clock_at_pause_var.set(x - 60)
        else:
            clock_at_pause_var.set(0)

    def cancel_clicked():
        root.destroy()

    def submit_clicked():
        root.destroy()
        on_submit(clock_at_pause_var.get())

    m_up_button = SizedButton(root, game_clock_m_up, u"Min \u2191", "Blue.TButton", 80, 200)
    m_up_button.grid(row=1, column=0)

    m_dn_button = SizedButton(root, game_clock_m_dn, u"Min \u2193", "Grey.TButton", 80, 200)
    m_dn_button.grid(row=2, column=0)

    s_up_button = SizedButton(root, game_clock_s_up, u"Sec \u2191", "Blue.TButton", 80, 200)
    s_up_button.grid(row=1, column=3)

    s_dn_button = SizedButton(root, game_clock_s_dn, u"Sec \u2193", "Grey.TButton", 80, 200)
    s_dn_button.grid(row=2, column=3)

    cancel_button = SizedButton(root, cancel_clicked, "CANCEL", "Red.TButton", 150, 400)
    cancel_button.grid(row=3, column=0, columnspan=2)

    submit_button = SizedButton(root, submit_clicked, "SUBMIT", "Green.TButton", 150, 400)
    submit_button.grid(row=3, column=2, columnspan=2)

    game_clock_var = tk.StringVar()

    def on_clock_changed(*args):
        x = clock_at_pause_var.get()
        game_clock_var.set('%d:%02d' % (x // 60, x % 60))
    on_clock_changed()

    clock_at_pause_var.trace('w', on_clock_changed)

    game_clock_new = SizedLabel(root, game_clock_var, "black", "blue", game_clock_font,
                                160, 400)
    game_clock_new.grid(row=1, rowspan=2, column=1, columnspan=2)

def EditScore(master, tb_offset, score, is_black, on_submit):
    root = tk.Toplevel(master, background='black')
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 480, 0, tb_offset))

    maybe_hide_cursor(root)

    root.overrideredirect(1)
    root.transient(master)


    header_font = (_font_name, 36)
    header_text = "BLACK" if is_black else "WHITE"
    header = SizedLabel(root, header_text, "black", "white", header_font, 50, 200)
    header.grid(row=0, columnspan=2, column=3)

    score_var = tk.IntVar(value=score)
    score_height = 120

    def dn():
        x = score_var.get()
        if x > 0:
            score_var.set(x - 1)

    dn_button = SizedButton(root, dn, "-", "Blue.TButton", score_height, 100)
    dn_button.grid(row=1, column=2)

    label_font = (_font_name, 96)
    label = SizedLabel(root, score_var, "black", "white", label_font, score_height, 200)
    label.grid(row=1, column=3, columnspan=2)

    def up():
        x = score_var.get()
        if x < 99:
            score_var.set(x + 1)

    up_button = SizedButton(root, up, "+", "Blue.TButton", score_height, 100)
    up_button.grid(row=1, column=5)

    def cancel_clicked():
        root.destroy()

    cancel_button = SizedButton(root, cancel_clicked, "CANCEL", "Red.TButton", 150, 400)
    cancel_button.grid(row=2, column=0, columnspan=4)

    def submit_clicked():
        root.destroy()
        on_submit(score_var.get())

    submit_button = SizedButton(root, submit_clicked, "SUBMIT", "Green.TButton", 150, 400)
    submit_button.grid(row=2, column=4, columnspan=4)

def IncrementScore(master, tb_offset, score, is_black, on_submit):
    root = tk.Toplevel(master, background='black')
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 480, 0, tb_offset))

    maybe_hide_cursor(root)

    root.overrideredirect(1)
    root.transient(master)

    space = tk.Frame(root, height=100, width=100, bg="black")
    space.grid(row=0, column=0)

    header_font = (_font_name, 36)
    color = "BLACK" if is_black else "WHITE"
    header_text = "SCORE {}?".format(color)
    header = SizedLabel(root, header_text, "black", "white", header_font, 50, 400)
    header.grid(row=1, columnspan=2, column=0)

    def no_clicked():
        root.destroy()

    no_button = SizedButton(root, no_clicked, "NO", "Red.TButton", 150, 400)
    no_button.grid(row=2, column=0)

    def yes_clocked():
        root.destroy()
        if score < 99:
            on_submit(score + 1)

    yes_button = SizedButton(root, yes_clocked, "YES", "Green.TButton", 150, 400)
    yes_button.grid(row=2, column=1)

def ScoreColumn(root, column, team_color, score_color, refresh_ms, get_score,
        score_changed, increment_score):
    score_height = 120
    score_width = 200

    label_font = (_font_name, 36)
    label_height = 50
    label_width = score_width

    button_height = 150
    button_width = score_width

    label = SizedLabel(root, team_color.upper(), score_color, "black",
                       label_font, label_height, label_width)
    label.grid(row=0, column=column)

    score_var = tk.IntVar()
    score_label = SizedButton(root, score_changed, score_var, "Huge.White.TButton",
                             score_height, score_width)
    score_label.grid(row=1, column=column)

    def refresh_score():
        score_var.set(get_score())
        score_label.after(refresh_ms, lambda: refresh_score())
    score_label.after(refresh_ms, lambda: refresh_score())

    button = SizedButton(root, increment_score, "SCORE", "Cyan.TButton",
                         button_height, button_width)
    button.grid(row=2, column=column)

    return root

def create_button_style(name, background, sz, foreground='black'):
    style = ttk.Style()
    style.configure(name, foreground=foreground, background=background,
        relief='flat', font=(_font_name, sz))
    style.map(name, background=[('active', background)])


def create_styles():
    huge_font_size = 80
    create_button_style('Huge.White.TButton', 'black', huge_font_size, foreground='white')
    create_button_style('Huge.Neon.TButton', 'black', huge_font_size, foreground='#000fff000')

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
        self.mgr.setGameStateFirstHalf()
        self.mgr.setGameClock(self.cfg.getint('game', 'half_play_duration'))

        self.root = tk.Tk()
        self.root.configure(background='black')

        maybe_hide_cursor(self.root)

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
                    lambda: self.edit_white_score(),
                    lambda: self.increment_white_score())

        self.center_column(refresh_ms)
        ScoreColumn(self.root, 2, 'black', 'blue',
                    refresh_ms, lambda: self.mgr.blackScore(),
                    lambda: self.edit_black_score(),
                    lambda: self.increment_black_score())

        def poll_clicker(self):
            if self.iomgr.readClicker():
                print("remote clicked")
                self.gong_clicked()
            else:
                self.iomgr.setSound(0)
            self.root.after(refresh_ms, lambda: poll_clicker(self))
        self.root.after(refresh_ms, lambda: poll_clicker(self))

    def center_column(self, refresh_ms):
        clock_height = 120
        clock_width = 400

        status_font = (_font_name, 36)
        status_height = 50
        status_width = clock_width


        self.status_var = tk.StringVar()
        self.status_var.set("FIRST HALF")

        status_label = SizedLabel(self.root, self.status_var, "black", "#000fff000", status_font,
                                  status_height, status_width)
        status_label.grid(row=0, column=1)

        self.game_clock_var = tk.StringVar()
        self.game_clock_var.set("##:##")
        self.game_clock_label = SizedButton(self.root, lambda: self.edit_time(),
                                            self.game_clock_var, "Huge.Neon.TButton",
                                            clock_height, clock_width)
        self.game_clock_label.grid(row=1, column=1)

        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

        time_button_var = tk.StringVar()
        self.timeout_mgr = TimeoutManager(time_button_var)
        half_play_duration = self.cfg.getint('game', 'half_play_duration')
        time_button = SizedButton(self.root,
                                  lambda: self.timeout_mgr.click(self.mgr, half_play_duration),
                                  time_button_var, "Yellow.TButton",
                                  150, clock_width)
        time_button.grid(row=2, column=1)

    def refresh_time(self):
        game_clock = self.mgr.gameClock()
        game_mins = game_clock // 60
        game_secs = game_clock % 60
        self.game_clock_var.set("%02d:%02d" % (game_mins, game_secs))

        half_play_duration = self.cfg.getint('game', 'half_play_duration')
        half_time_duration = self.cfg.getint('game', 'half_time_duration')

        if game_clock <= 0 and self.mgr.gameClockRunning():
            if self.mgr.gameStateFirstHalf():
                self.mgr.setGameStateHalfTime()
                self.mgr.setGameClock(half_time_duration)
                self.gong_clicked()
            elif self.mgr.gameStateHalfTime():
                self.mgr.setGameStateSecondHalf()
                self.mgr.setGameClock(half_play_duration)
                self.gong_clicked()
            elif self.mgr.gameStateSecondHalf():
                self.gong_clicked()
                self.timeout_mgr.set_game_over(self.mgr)

        if self.mgr.timeoutStateRef():
            self.status_var.set("TIMEOUT")
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
        self.root.after(1000, lambda: self.iomgr.setSound(0))

    def edit_white_score(self):
        EditScore(self.root, self.tb_offset, self.mgr.whiteScore(),
                        False, lambda x: self.mgr.setWhiteScore(x))

    def edit_black_score(self):
        EditScore(self.root, self.tb_offset, self.mgr.blackScore(),
                        True, lambda x: self.mgr.setBlackScore(x))

    def increment_white_score(self):
        IncrementScore(self.root, self.tb_offset, self.mgr.whiteScore(),
                        False, lambda x: self.mgr.setWhiteScore(x))

    def increment_black_score(self):
        IncrementScore(self.root, self.tb_offset, self.mgr.blackScore(),
                        True, lambda x: self.mgr.setBlackScore(x))

    def edit_time(self):
        was_running = self.mgr.gameClockRunning()
        self.mgr.setGameClockRunning(False)
        clock_at_pause = self.mgr.gameClock();

        def submit_clicked(game_clock):
            self.mgr.setGameClock(game_clock)
            self.mgr.setGameClockRunning(was_running)

        EditTime(self.root, self.tb_offset, clock_at_pause, submit_clicked)

