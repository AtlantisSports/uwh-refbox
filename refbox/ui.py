import tkinter as tk
from tkinter import ttk
from configparser import ConfigParser
import os
from .timeoutmanager import TimeoutManager
from uwh.gamemanager import GameManager, GameState, TeamColor, Penalty, TimeoutState
from functools import partial
import time

_font_name = 'Consolas'

FIRST_PREGAME_LEN = 10 * 60

def RefboxConfigParser():
    defaults = {
        # hardware
        'screen_x': '800',
        'screen_y': '480',
        'version': '1',
        'has_xbee': 'False',
        'white_on_right': 'True',

        # xbee
        'port': '/dev/tty.usbserial-DN03ZRU8',
        'baud': '9600',
        'clients': '[]',
        'ch': '000C',
        'id': '000D',

        # game
        'half_play_duration': '900',
        'half_time_duration': '180',
        'team_timeout_duration': '60',
        'team_timeouts_allowed': '1',
        'has_overtime': 'False',
        'ot_half_play_duration': '300',
        'pre_overtime_break': '180',
        'overtime_break_duration': '60',
        'pre_sudden_death_duration': '60',
        'pre_sudden_death_duration': '60',
        'sudden_death_allowed': 'False',
        'max_sudden_death_duration': '1800',
        'overtime_timeouts_allowed': 'False',
        'team_timeouts_per_half': 'True',
        'pool' : '1',
        'tid' : '16',
        'uwhscores_url' : 'http://uwhscores.com/api/v1/',
    }
    parser = ConfigParser(defaults=defaults)
    parser.add_section('hardware')
    parser.add_section('xbee')
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
    sf._inner = l
    return sf


def SizedButton(root, callback, text, style, height, width):
    sf = sized_frame(root, height, width)

    if isinstance(text, str):
        b = ttk.Button(sf, text=text, command=callback, style=style)
    else:
        b = ttk.Button(sf, textvariable=text, command=callback, style=style)

    b.pack(fill=tk.BOTH, expand=1)
    return sf

def is_rpi():
    return os.uname().machine == 'armv7l'

def maybe_hide_cursor(root):
    # Don't show a cursor on Pi.
    if is_rpi():
        root.configure(cursor='none')

class TimeEditor(object):
    def __init__(self, master, tb_offset, clock_at_pause, on_submit, on_cancel, cfg, mgr):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                           cfg.getint('hardware', 'screen_y'),
                                           0, 0))

        self.mgr = mgr

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit
        self.on_cancel = on_cancel

        space = tk.Frame(self.root, height=50, width=100, bg="black")
        space.grid(row=0, column=0)

        if mgr.gameState() == GameState.game_over:
            clock_at_pause += 3 * 60

        self.clock_at_pause_var = tk.IntVar(value=clock_at_pause)

        game_clock_font = (_font_name, 72)

        m_up_button = SizedButton(self.root, self.game_clock_m_up, u"Min \u2191",
                                  "LightBlue.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        m_up_button.grid(row=1, column=0)

        m_dn_button = SizedButton(self.root, self.game_clock_m_dn, u"Min \u2193",
                                  "Grey.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        m_dn_button.grid(row=2, column=0)

        s_up_button = SizedButton(self.root, self.game_clock_s_up, u"Sec \u2191",
                                  "LightBlue.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        s_up_button.grid(row=1, column=3)

        s_dn_button = SizedButton(self.root, self.game_clock_s_dn, u"Sec \u2193",
                                  "Grey.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        s_dn_button.grid(row=2, column=3)

        cancel_button = SizedButton(self.root, self.cancel_clicked, "CANCEL",
                                    "Red.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        cancel_button.grid(row=3, column=0, columnspan=2)

        submit_button = SizedButton(self.root, self.submit_clicked, "SUBMIT",
                                    "Green.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        submit_button.grid(row=3, column=2, columnspan=2)

        self.game_clock_var = tk.StringVar()

        self.clock_at_pause_var.trace('w', self.on_clock_changed)
        self.on_clock_changed()

        game_clock_new = SizedLabel(self.root, self.game_clock_var, "black", "blue",
                                    game_clock_font,
                                    160, cfg.getint('hardware', 'screen_x') / 2)
        game_clock_new.grid(row=1, rowspan=2, column=1, columnspan=2)

    def on_clock_changed(self, *args):
        x = self.clock_at_pause_var.get()
        self.game_clock_var.set('%d:%02d' % (x // 60, x % 60))

    def game_clock_s_up(self):
        x = self.clock_at_pause_var.get()
        self.clock_at_pause_var.set(x + 1)

    def game_clock_s_dn(self):
        x = self.clock_at_pause_var.get()
        if self.mgr.gameState() == GameState.game_over:
            if x > 3 * 60:
                self.clock_at_pause_var.set(x - 1)
        else:
            if x > 0:
                self.clock_at_pause_var.set(x - 1)

    def game_clock_m_up(self):
        x = self.clock_at_pause_var.get()
        self.clock_at_pause_var.set(x + 60)

    def game_clock_m_dn(self):
        x = self.clock_at_pause_var.get()
        if self.mgr.gameState() == GameState.game_over:
            self.clock_at_pause_var.set(max(x - 60, 3 * 60))
        else:
            if x - 60 >= 0:
                self.clock_at_pause_var.set(x - 60)
            else:
                self.clock_at_pause_var.set(0)

    def cancel_clicked(self):
        self.on_cancel()
        self.root.destroy()

    def submit_clicked(self):
        if self.mgr.gameState() == GameState.game_over:
            self.on_submit(self.clock_at_pause_var.get() - 3 * 60)
        else:
            self.on_submit(self.clock_at_pause_var.get())
        self.root.destroy()

    def wait(self):
        self.root.wait_window()


class ScoreEditor(object):
    def __init__(self, master, tb_offset, reason, black, white, on_submit, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                           cfg.getint('hardware', 'screen_y'),
                                           0, 0))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit

        score_font = (_font_name, 72)

        space = tk.Frame(self.root, height=50, width=100, bg="black")
        space.grid(row=0, column=0)

        reason_label = SizedLabel(self.root, reason, "black", "white",
                                  score_font, 50, cfg.getint('hardware', 'screen_x'))
        reason_label.grid(row=1, column=0, columnspan=4)

        space = tk.Frame(self.root, height=50, width=100, bg="black")
        space.grid(row=2, column=0)

        w_up_button = SizedButton(self.root, self.score_w_up, u"White \u2191",
                                  "LightBlue.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        w_up_button.grid(row=3, column=0)

        w_dn_button = SizedButton(self.root, self.score_w_dn, u"White \u2193",
                                  "Grey.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        w_dn_button.grid(row=4, column=0)

        b_up_button = SizedButton(self.root, self.score_b_up, u"Black \u2191",
                                  "LightBlue.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        b_up_button.grid(row=3, column=3)

        b_dn_button = SizedButton(self.root, self.score_b_dn, u"Black \u2193",
                                  "Grey.TButton",
                                  80, cfg.getint('hardware', 'screen_x') / 4)
        b_dn_button.grid(row=4, column=3)

        cancel_button = SizedButton(self.root, self.cancel_clicked, "CANCEL",
                                    "Red.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        cancel_button.grid(row=5, column=0, columnspan=2)

        submit_button = SizedButton(self.root, self.submit_clicked, "SUBMIT",
                                    "Green.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        submit_button.grid(row=5, column=2, columnspan=2)

        self.white_display_var = tk.StringVar()
        white_display = SizedLabel(self.root, self.white_display_var, "black", "white",
                                    score_font,
                                    160, cfg.getint('hardware', 'screen_x') / 4)
        white_display.grid(row=3, rowspan=2, column=1)

        self.black_display_var = tk.StringVar()
        black_display = SizedLabel(self.root, self.black_display_var, "black", "blue",
                                    score_font,
                                    160, cfg.getint('hardware', 'screen_x') / 4)
        black_display.grid(row=3, rowspan=2, column=2)

        self.black_var = tk.IntVar(value=black)
        self.white_var = tk.IntVar(value=white)
        self.black_var.trace('w', self.on_score_changed)
        self.white_var.trace('w', self.on_score_changed)
        self.on_score_changed()

    def on_score_changed(self, *args):
        b = self.black_var.get()
        w = self.white_var.get()
        self.black_display_var.set(str(b))
        self.white_display_var.set(str(w))

    def score_b_up(self):
        x = self.black_var.get()
        self.black_var.set(min(x + 1, 99))

    def score_b_dn(self):
        x = self.black_var.get()
        self.black_var.set(max(x - 1, 0))

    def score_w_up(self):
        x = self.white_var.get()
        self.white_var.set(min(x + 1, 99))

    def score_w_dn(self):
        x = self.white_var.get()
        self.white_var.set(max(x - 1, 0))

    def cancel_clicked(self):
        self.root.destroy()

    def submit_clicked(self):
        self.on_submit(self.black_var.get(), self.white_var.get())
        self.root.destroy()

    def wait(self):
        self.root.wait_window()


class ConfirmDialog(object):
    def __init__(self, master, tb_offset, prompt, on_yes, on_no, cfg,
                 yes_txt='YES', no_txt='NO', y_offset=0):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y') - y_offset,
                                                0, tb_offset + y_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_yes = on_yes
        self.on_no = on_no

        space = tk.Frame(self.root, height=100, width=100, bg="black")
        space.grid(row=0, column=0)

        header_font = (_font_name, 20)
        header = SizedLabel(self.root, prompt, "black", "white", header_font,
                            200, cfg.getint('hardware', 'screen_x'))
        header.grid(row=1, columnspan=2, column=0)

        no_button = SizedButton(self.root, self.no_clicked, no_txt, "Red.TButton",
                                150, cfg.getint('hardware', 'screen_x') / 2)
        no_button.grid(row=2, column=0)

        yes_button = SizedButton(self.root, self.yes_clicked, yes_txt, "Green.TButton",
                                 150, cfg.getint('hardware', 'screen_x') / 2)
        yes_button.grid(row=2, column=1)

    def no_clicked(self):
        self.on_no()
        self.root.destroy()

    def yes_clicked(self):
        self.on_yes()
        self.root.destroy()

    def wait(self):
        self.root.wait_window()


class ScoreIncrementer(object):
    def __init__(self, master, tb_offset, is_black, on_submit, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit

        space = tk.Frame(self.root, height=100, width=100, bg="black")
        space.grid(row=0, column=0)

        # Player Selection
        self._numpad = PlayerSelectNumpad(self.root, '')
        self._numpad.grid(row=1, column=0)

        header_font = (_font_name, 36)
        color = "BLACK" if is_black else "WHITE"
        header_text = "SCORE {}?".format(color)
        header = SizedLabel(self.root, header_text, "black", "white", header_font,
                            50, cfg.getint('hardware', 'screen_x')/ 2)
        header.grid(row=1, column=1)

        no_button = SizedButton(self.root, self.no_clicked, "NO", "Red.TButton",
                                150, cfg.getint('hardware', 'screen_x') / 2)
        no_button.grid(row=2, column=0)

        yes_button = SizedButton(self.root, self.yes_clicked, "YES", "Green.TButton",
                                 150, cfg.getint('hardware', 'screen_x') / 2)
        yes_button.grid(row=2, column=1)

    def no_clicked(self):
        self.root.destroy()

    def yes_clicked(self):
        self.on_submit(self._numpad.get_value())
        self.root.destroy()

    def wait(self):
        self.root.wait_window()


def ScoreColumn(root, column, team_color, score_color, refresh_ms, get_score,
                score_changed, increment_score, cfg):
    score_height = 120
    score_width = cfg.getint('hardware', 'screen_x') / 4

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


class PenaltyButton(object):
    def __init__(self, root, penalty, width, height, refresh_ms, mgr, edit_clicked):
        self.penalty = penalty
        self.refresh_ms = refresh_ms
        self.mgr = mgr
        self.var = tk.StringVar()
        self.button = SizedButton(root, edit_clicked, self.var, "Small.White.TButton",
                                  height, width)
        self.button.after(refresh_ms, self.refresh)

    def refresh(self):
        remaining = self.penalty.timeRemaining(self.mgr)
        if self.penalty.dismissed():
            time_str = "Dismissed"
        elif remaining != 0:
            time_str = "%d:%02d" % (remaining // 60, remaining % 60)
        else:
            time_str = "Served"
        self.var.set("#{} - {}".format(self.penalty.player(), time_str))
        self.button.after(self.refresh_ms, self.refresh)


class PenaltiesColumn(object):
    def __init__(self, root, col, team_color, refresh_ms, mgr, edit_penalty,
                 add_penalty, cfg):
        self.edit_penalty = edit_penalty
        self.add_penalty = add_penalty
        self.selection = None
        self.mgr = mgr
        self.team_color = team_color
        self.refresh_ms = refresh_ms

        self.buttons = []

        self.col_width = cfg.getint('hardware', 'screen_x') / 4

        self.outer = sized_frame(root, 380, self.col_width)
        self.outer.grid(row=3, column=col)

        self.canvas = tk.Canvas(self.outer, background="#cccccc")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.outer, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand = self.scrollbar.set)

        self.canvas.bind('<Configure>', lambda _: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.frame, anchor='nw')

        button_height = 70
        button_width = self.col_width

        add = SizedButton(root, self.add_clicked, "Penalty", "Red.TButton",
                          button_height, button_width)
        add.grid(row=4, column=col)

        for p in self.mgr.penalties(self.team_color):
            self.add_button(p)

    def redraw(self):
        for b in self.buttons:
            b.button.destroy()

        for p in self.mgr.penalties(self.team_color):
            self.add_button(p)

    def add_clicked(self):
        self.add_penalty()

    def edit_clicked(self, p):
        self.edit_penalty(p)

    def add_button(self, p):
        b = PenaltyButton(self.frame, p, self.col_width, 50,
                          self.refresh_ms, self.mgr, partial(self.edit_penalty, p))
        b.button.pack()
        self.buttons.append(b)


class SettingsView(object):
    def __init__(self, parent, tb_offset, height, width, mgr, cfg, uwhscores):
        self.parent = parent
        self.root = parent.root
        self.tb_offset = tb_offset
        self.mgr = mgr
        self.cfg = cfg
        self.uwhscores = uwhscores

        self.games = []

        tid = cfg.get('game', 'tid')
        pool = cfg.get('game', 'pool')

        self.outer = sized_frame(self.root, height, width)
        self.outer.grid(row=3, column=1, rowspan=2)

        self.info = sized_frame(self.outer, height / 2, width)
        self.info.grid(row=0, column=0)

        label_font = ("Courier New", 12)
        self.game_info_var = tk.StringVar()
        game_info = SizedLabel(self.info, self.game_info_var, "black", "white",
                               label_font, height=height / 2, width=width)
        game_info._inner.config(justify=tk.LEFT)
        game_info.grid(row=0, column=0)

        self.game_list = sized_frame(self.outer, height / 2, width)
        self.game_list.grid(row=1, column=0)

        scrollbar = tk.Scrollbar(self.game_list, width=30)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.game_list, font=(_font_name, 18),
                                  selectmode=tk.SINGLE)
        self.listbox.pack(expand=1, fill=tk.BOTH)
        self.cur_selection = None

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        def today(g):
            from datetime import datetime, date
            return (datetime.strptime(g['start_time'],
                                      "%Y-%m-%dT%H:%M:%S").date() ==
                    date.today())

        def response(games):
            self.games = [g for g in games if g['pool'] == pool and today(g)]

            for game in self.games:
                self.listbox.insert(tk.END, self.desc(game))

            if len(self.games) > 0:
                self.select(0)
                self.setup_game()

            self.outer.after(250, self.poll)

        if self.uwhscores:
            self.uwhscores.get_game_list(tid, response)

    def desc(self, game):
        return "{}{} - {} vs {}".format(game['game_type'], game['gid'],
                                        game['white'], game['black'])

    def setup_game(self):
        if not self.parent.not_yet_started:
            self.mgr.setBlackScore(0)
            self.mgr.setWhiteScore(0)
            self.mgr.setTimeoutState(TimeoutState.none)
            self.mgr.deleteAllPenalties()
            self.mgr.delAllGoals()
            self.parent.redraw_penalties()
            self.mgr.setGameState(GameState.pre_game)
            self.mgr.setGameClock(3 * 60)


    def select(self, idx):
        self.game = self.games[idx]
        self.parent.set_game_info(self.game)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.cur_selection = (idx,)
        self.mgr.setGid(self.game['gid'])

        rules = self.game['timing_rules']
        info =  self.desc(self.game) + "\n"
        info = "Game:  " + self.game['game_type'] + str(self.game['gid']) + "\n"
        info += "White: " + self.game['white'] + "\n"
        info += "Black: " + self.game['black'] + "\n"
        info += "\n"
        info += "1st/2nd Half:  " + self.fmt_time(self.parent.half_play_duration()) + "\n"
        info += "Half Time:     " + self.fmt_time(self.parent.half_time_duration()) + "\n"
        #info += "Minimum Break: " + self.fmt_time(rules['min_game_break']) + "\n"
        info += "\n"
        if self.parent.has_overtime():
            info += "Overtime:        Yes\n"
        else:
            info += "Overtime:         No\n"
        if self.parent.has_sudden_death():
            info += "Sudden Death:    Yes\n"
        else:
            info += "Sudden Death:     No\n"

        to_allowed = self.parent.team_timeouts_allowed()
        if to_allowed > 0:
            info += "Timeouts Allowed:    " + str(to_allowed)
            if self.parent.team_timeouts_per_half():
                info += " / team / half\n"
            else:
                info += " / team / game\n"
            info += "Timeout Duration:    " + self.fmt_time(self.parent.team_timeout_duration())

        self.game_info_var.set(info)

    def fmt_time(self, time):
        return "%2d:%02d" % (time // 60, time % 60)

    def poll(self):
        now = self.listbox.curselection()
        if now != self.cur_selection and now != ():
            temp = self.cur_selection
            self.cur_selection = now

            def on_yes():
                self.select(now[0]-1)
                self.setup_game()
                self.parent.gong_clicked("Change of Game", 3000)
                self.parent.timeout_mgr.reset(self.mgr)
            def on_no():
                self.select(now[0])

            ConfirmDialog(self.root, self.tb_offset,
                          "Switching to {}.\n\n\nWARNING: Also reset the game?"
                              .format(self.desc(self.games[now[0]])),
                          on_yes, on_no, self.cfg)

        self.outer.after(250, self.poll)

    def next_game(self):
        if self.cur_selection:
            next_idx = self.cur_selection[0] + 1
            if next_idx < len(self.games):
                self.select(next_idx)
                self.mgr.setGid(int(self.games[next_idx]['gid']))


class PlayerSelectNumpad(tk.Frame):
    def __init__(self, root, content):
        button_width = 75
        button_height = 75
        tk.Frame.__init__(self, root, height=button_height * 5,
                          width=button_width * 3, bg="black")

        self._content_var = tk.StringVar()

        label_font = (_font_name, 18)
        label = SizedLabel(self, self._content_var, "black", "white", label_font,
                           height=button_height, width=button_width * 3)
        label.grid(row=0, column=0, columnspan=3)

        grid = [[7, 8, 9],
                [4, 5, 6],
                [1, 2, 3],
                [0, "del"]]

        self._content = '{}'.format(content)
        self.clicked(None)

        for y in range(0, len(grid)):
            for x in range(0, len(grid[y])):
                val = grid[y][x]
                w = button_width * 2 if val == "del" else button_width
                h = button_height
                btn = SizedButton(self, partial(self.clicked, val),
                                  '{}'.format(val), "LightBlue.TButton", h, w)
                btn.config(border=1)
                if val == "del":
                    btn.grid(row=y + 1, column=x, columnspan=2)
                else:
                    btn.grid(row=y + 1, column=x)

    def clicked(self, val):
        if val == "del":
            if self._content != '':
                self._content = self._content[:-1]
        elif val is not None:
            self._content += '{}'.format(val)
        if self._content == '':
            self._content_var.set('Player ?')
        else:
            self._content_var.set('Player {}'.format(self._content))

    def get_value(self):
        return self._content


class PenaltyEditor(object):
    def __init__(self, master, tb_offset, mgr, cfg, team_color, on_delete, on_submit,
                 penalty=None, y_offset=0):
        self._team = team_color

        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y')-y_offset,
                                                0, tb_offset + y_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_delete = on_delete
        self.on_submit = on_submit

        title_str = "Penalty"
        label_font = (_font_name, 48)
        title = SizedLabel(self.root, title_str, "black", "white", label_font,
                           height=100, width=cfg.getint('hardware', 'screen_y'))
        title.grid(row=0, column=0, columnspan=3)

        self._penalty = penalty or Penalty('', team_color, 60)
        self._duration = tk.IntVar()
        self._duration.set(self._penalty.duration())

        frame_height = 75 * 5
        frame_width = 200

        # Player Color
        color_frame = tk.Frame(self.root, height=frame_height, width=frame_width,
                              bg="grey")
        color_frame.grid(row=1, column=0)
        self._white = SizedButton(color_frame, partial(self.color_select, TeamColor.white),
                                    "White", "White.TButton", frame_height / 2,
                                    frame_width)
        self._white.grid(row=0, column=0)

        self._black = SizedButton(color_frame, partial(self.color_select, TeamColor.black),
                                    "Black", "Blue.TButton", frame_height / 2,
                                    frame_width)
        self._black.grid(row=1, column=0)
        self.color_select(self._penalty.team())

        # Player Selection
        self._numpad = PlayerSelectNumpad(self.root, self._penalty.player())
        self._numpad.grid(row=1, column=1)

        # Penalty Duration
        time_frame = tk.Frame(self.root, height=frame_height, width=frame_width,
                              bg="grey")
        time_frame.grid(row=1, column=2)
        self._one_min = SizedButton(time_frame, partial(self.time_select, 60),
                                    "1 min", "Yellow.TButton", frame_height / 4,
                                    frame_width)
        self._one_min.grid(row=1, column=0)

        self._two_min = SizedButton(time_frame, partial(self.time_select, 120),
                                    "2 min", "Yellow.TButton", frame_height / 4,
                                    frame_width)
        self._two_min.grid(row=2, column=0)

        self._five_min = SizedButton(time_frame, partial(self.time_select, 300),
                                     "5 min", "Yellow.TButton", frame_height / 4,
                                     frame_width)
        self._five_min.grid(row=3, column=0)

        self._dismissal = SizedButton(time_frame, partial(self.time_select, -1),
                                      "Dismissal", "Red.TButton", frame_height / 4,
                                      frame_width)
        self._dismissal.grid(row=4, column=0)
        self.time_select(self._penalty.duration())

        space = tk.Frame(self.root, height=50, width=50, bg='black')
        space.grid(row=2, column=0, columnspan=3)

        frame_height = 100
        frame_width = cfg.getint('hardware', 'screen_x')

        # Actions
        submit_frame = tk.Frame(self.root, height=frame_height, width=frame_width,
                                bg="dark grey")
        submit_frame.grid(row=3, column=0, columnspan=3)

        cancel = SizedButton(submit_frame, self.cancel_clicked, "Cancel",
                             "Yellow.TButton", frame_height, frame_width / 3)
        cancel.grid(row=0, column=0)

        delete = SizedButton(submit_frame, self.delete_clicked,
                             "Delete", "Red.TButton", frame_height, frame_width / 3)
        delete.grid(row=0, column=1)

        submit = SizedButton(submit_frame, self.submit_clicked, "Submit",
                             "Green.TButton", frame_height, frame_width / 3)
        submit.grid(row=0, column=2)

    def time_select(self, kind):
        self._one_min.config(relief=tk.RAISED, border=6)
        self._two_min.config(relief=tk.RAISED, border=6)
        self._five_min.config(relief=tk.RAISED, border=6)
        self._dismissal.config(relief=tk.RAISED, border=6)
        if kind == 60:
            self._one_min.config(relief=tk.SUNKEN)
        elif kind == 120:
            self._two_min.config(relief=tk.SUNKEN)
        elif kind == 300:
            self._five_min.config(relief=tk.SUNKEN)
        elif kind == -1:
            self._dismissal.config(relief=tk.SUNKEN)
        self._duration.set(kind)

    def color_select(self, kind):
        self._white.config(relief=tk.RAISED, border=6)
        self._black.config(relief=tk.RAISED, border=6)
        if kind == TeamColor.white:
            self._white.config(relief=tk.SUNKEN)
        else:
            self._black.config(relief=tk.SUNKEN)
        self._team = kind

    def cancel_clicked(self):
        self.root.destroy()

    def delete_clicked(self):
        self.root.destroy()
        self.on_delete(self._penalty)

    def submit_clicked(self):
        self.root.destroy()
        self.on_submit(self._team, self._numpad.get_value(), self._duration.get())

    def wait(self):
        self.root.wait_window()


class TimeoutEditor(object):
    def __init__(self, root, normal_view, tb_offset, mgr, cfg, on_ref, on_white, on_black, on_shot):
        self.root = tk.Toplevel(root, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(root)

        timeout_mgr = normal_view.timeout_mgr

        self.on_ref = on_ref
        self.on_white = on_white
        self.on_black = on_black
        self.on_shot = on_shot

        frame_height = 500
        frame_width = cfg.getint('hardware', 'screen_x')

        space = tk.Frame(self.root, height=100, width=frame_width, bg="black")
        space.grid(row=0, column=0, columnspan=4)

        space = tk.Frame(self.root, height=frame_height, width=0,
                         bg="black")
        space.grid(row=1, column=0)

        submit_frame = tk.Frame(self.root, height=frame_height, width=frame_width / 2,
                                bg="dark grey")
        submit_frame.grid(row=1, column=1, columnspan=2)


        # Actions
        row = 0
        ref = SizedButton(submit_frame, self.ref_clicked, "Ref Timeout",
                             "Yellow.TButton", frame_height / 5, frame_width / 2)
        ref.grid(row=row, column=0)
        row += 1

        if (normal_view.team_timeouts_allowed() and
            (mgr.gameState() == GameState.first_half or
             mgr.gameState() == GameState.second_half or
             (normal_view.overtime_timeouts_allowed() and
              (mgr.gameState() == GameState.sudden_death or
               mgr.gameState() == GameState.ot_first or
               mgr.gameState() == GameState.ot_second)))):
            if timeout_mgr.timeout_allowed(TeamColor.white):
                white = SizedButton(submit_frame, self.white_clicked,
                                    "White Timeout", "White.TButton",
                                    frame_height / 5, frame_width / 2)
                white.grid(row=row, column=0)
                row += 1

            if timeout_mgr.timeout_allowed(TeamColor.black):
                black = SizedButton(submit_frame, self.black_clicked,
                                    "Black Timeout", "Blue.TButton",
                                    frame_height / 5, frame_width / 2)
                black.grid(row=row, column=0)
                row += 1

        shot = SizedButton(submit_frame, self.shot_clicked, "Penalty Shot",
                             "Cyan.TButton", frame_height / 5, frame_width / 2)
        shot.grid(row=row, column=0)
        row += 1

        cancel = SizedButton(submit_frame, self.cancel_clicked, "Cancel",
                             "Red.TButton", frame_height / 5, frame_width / 2)
        cancel.grid(row=row, column=0)
        row += 1

    def ref_clicked(self):
        self.root.destroy()
        self.on_ref()

    def white_clicked(self):
        self.root.destroy()
        self.on_white()

    def black_clicked(self):
        self.root.destroy()
        self.on_black()

    def shot_clicked(self):
        self.root.destroy()
        self.on_shot()

    def cancel_clicked(self):
        self.root.destroy()


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
    create_button_style('LightBlue.TButton', 'light blue', font_size)
    create_button_style('Blue.TButton', 'dark blue', font_size, foreground='white')
    create_button_style('Red.TButton', 'red', font_size)
    create_button_style('White.TButton', 'white', font_size)
    create_button_style('Dark.White.TButton', 'light grey', font_size)
    create_button_style('Yellow.TButton', 'yellow', font_size)

    font_size = 14
    create_button_style('Small.White.TButton', 'white', font_size)


class NormalView(object):

    def __init__(self, mgr, iomgr, NO_TITLE_BAR, cfg=None, uwhscores=None):
        self.mgr = GameManager([mgr])
        self.iomgr = iomgr
        self.cfg = cfg or RefboxConfigParser()
        self.uwhscores = uwhscores
        self.game_info = None
        self.not_yet_started = True
        self.mgr.setGameState(GameState.pre_game)
        self.mgr.setGameClock(FIRST_PREGAME_LEN)

        self.root = tk.Tk()
        self.root.configure(background='black')

        maybe_hide_cursor(self.root)

        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(self.cfg.getint('hardware', 'screen_x'),
                                                self.cfg.getint('hardware', 'screen_y'),
                                                0, 0))
        if NO_TITLE_BAR:
            self.root.overrideredirect(1)
            self.tb_offset = 0
        else:
            self.tb_offset = 70

        refresh_ms = 50

        create_styles()
        ScoreColumn(self.root, 0, 'white', 'white',
                    refresh_ms, lambda: self.mgr.whiteScore(),
                    lambda: self.edit_score(),
                    lambda: self.increment_white_score(),
                    self.cfg)

        self.center_column(refresh_ms)
        ScoreColumn(self.root, 2, 'black', 'blue',
                    refresh_ms, lambda: self.mgr.blackScore(),
                    lambda: self.edit_score(),
                    lambda: self.increment_black_score(),
                    self.cfg)

        def poll_clicker(self):
            if self.iomgr.readClicker():
                print("remote clicked")
            else:
                self.iomgr.setSound(0)
            self.root.after(refresh_ms, lambda: poll_clicker(self))
        self.root.after(refresh_ms, lambda: poll_clicker(self))

        self.penalties = [None, None]
        if self.cfg.getint('hardware', 'version') == 2:
            self.penalties = [None, None]
            wht =  PenaltiesColumn(self.root, 0, TeamColor.white, refresh_ms, self.mgr,
                                   lambda idx: self.edit_penalty(TeamColor.white, idx),
                                   lambda: self.add_penalty(TeamColor.white), self.cfg)
            self.penalties[TeamColor.white] = wht
            blk = PenaltiesColumn(self.root, 2, TeamColor.black, refresh_ms, self.mgr,
                                  lambda idx: self.edit_penalty(TeamColor.black, idx),
                                  lambda: self.add_penalty(TeamColor.black), self.cfg)
            self.penalties[TeamColor.black] = blk

    def redraw_penalties(self):
        white = self.penalties[TeamColor.white]
        if white:
            white.redraw()

        black = self.penalties[TeamColor.black]
        if black:
            black.redraw()

    def edit_penalty(self, team_color, p):
        def submit_clicked(new_team, player, duration):
            try:
                p.setTeam(new_team)
                p.setPlayer(int(player))
            except ValueError:
                pass
            p.setDuration(duration)
            self.redraw_penalties()
        def delete_clicked(penalty):
            self.mgr.delPenalty(penalty)
            self.redraw_penalties()
        PenaltyEditor(self.root, self.tb_offset, self.mgr, self.cfg, team_color,
                      delete_clicked, submit_clicked, p).wait()

    def add_penalty(self, team_color):
        def submit_clicked(self, new_team, player, duration):
            try:
                player = int(player)
            except ValueError:
                player = -1
            p = Penalty(player, new_team, duration)

            ConfirmDialog(self.root, self.tb_offset, "",
                          lambda:None,
                          lambda:self.add_penalty(team_color),
                          self.cfg,
                          "Done", "More Penalties",
                          y_offset=150).wait()

            self.mgr.addPenalty(p)
            self.redraw_penalties()
        PenaltyEditor(self.root, self.tb_offset, self.mgr, self.cfg, team_color,
                      lambda x: None, partial(submit_clicked, self),
                      y_offset=150).wait()

    def timeout_clicked(self):
        def ref_clicked():
            self.timeout_mgr.click(self.mgr, TimeoutState.ref)
            self.redraw_penalties()
        def shot_clicked():
            self.timeout_mgr.click(self.mgr, TimeoutState.penalty_shot)
            self.redraw_penalties()
        def white_clicked():
            self.timeout_mgr.timeout_used(TeamColor.white)
            self.timeout_mgr.click(self.mgr, TimeoutState.white)
            self.redraw_penalties()
        def black_clicked():
            self.timeout_mgr.timeout_used(TeamColor.black)
            self.timeout_mgr.click(self.mgr, TimeoutState.black)
            self.redraw_penalties()
        if (self.timeout_mgr.ready_to_start() or
            self.timeout_mgr.ready_to_reset() or
            self.timeout_mgr.ready_to_resume()):
            if self.mgr.timeoutState() != TimeoutState.ref:
                self.gong_clicked("Start of First Game (or Resume?)", 1000)
            self.timeout_mgr.click(self.mgr, TimeoutState.none)
            self.redraw_penalties()
        else:
            TimeoutEditor(self.root, self, self.tb_offset, self.mgr, self.cfg,
                          ref_clicked, white_clicked, black_clicked, shot_clicked)

    def center_column(self, refresh_ms):
        clock_height = 120
        clock_width = self.cfg.getint('hardware', 'screen_x') / 2

        status_font = (_font_name, 36)
        status_height = 50
        status_width = clock_width


        self.status_var = tk.StringVar()
        self.status_var.set("FIRST HALF")

        status_label = SizedLabel(self.root, self.status_var, "black", "#000fff000", status_font,
                                  status_height, status_width)
        status_label.grid(row=0, column=1)
        self.status_label = status_label

        self.game_clock_var = tk.StringVar()
        self.game_clock_var.set("##:##")
        self.game_clock_label = SizedButton(self.root, lambda: self.edit_time(),
                                            self.game_clock_var, "Huge.Neon.TButton",
                                            clock_height, clock_width)
        self.game_clock_label.grid(row=1, column=1)

        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

        time_button_var = tk.StringVar()
        self.timeout_mgr = TimeoutManager(time_button_var, lambda: self.team_timeout_duration())
        time_button = SizedButton(self.root,
                                  lambda: self.timeout_clicked(),
                                  time_button_var, "Yellow.TButton",
                                  150, clock_width)
        time_button.grid(row=2, column=1)

        self.settings_view = SettingsView(self, self.tb_offset, 450, clock_width,
                                          self.mgr, self.cfg, self.uwhscores)
        self.timeout_mgr.add_reset_handler(self.settings_view.next_game)

    def post_score(self, is_final):
        if self.game_info is not None:
            if is_final:
                self.uwhscores.post_score(
                    self.game_info['tid'],
                    self.game_info['gid'],
                    self.mgr.blackScore(),
                    self.mgr.whiteScore(),
                    self.game_info['black_id'],
                    self.game_info['white_id'])

    def game_break(self, new_duration, new_state):
        self.mgr.deleteServedPenalties()
        self.mgr.pauseOutstandingPenalties()
        self.redraw_penalties()
        self.mgr.setGameClock(new_duration)
        self.mgr.setGameState(new_state)

    def play_ready(self, new_duration, new_state):
        self.mgr.deleteServedPenalties()
        self.redraw_penalties()
        self.mgr.setGameClockRunning(False)
        self.mgr.setGameClock(new_duration)
        self.mgr.setGameState(new_state)

    def confirm_scores(self):
        def edit_scores():
            def set_score(black, white):
                self.mgr.setBlackScore(black)
                self.mgr.setWhiteScore(white)
            ScoreEditor(self.root, self.tb_offset, "Edit Final Scores",
                        self.mgr.blackScore(),
                        self.mgr.whiteScore(), set_score, self.cfg).wait()

        ConfirmDialog(self.root, self.tb_offset,
                      "Final score correct?\n\nWhite: %d Black: %d"
                         % (self.mgr.whiteScore(), self.mgr.blackScore()),
                      lambda:None, edit_scores, self.cfg).wait()

    def game_over(self):
        self.mgr.setGameClockRunning(False)
        self.mgr.setGameClock(0)

        self.post_score(True)
        self.mgr.setGameState(GameState.game_over)
        self.mgr.deleteAllPenalties()
        self.mgr.delAllGoals()
        self.redraw_penalties()
        self.timeout_mgr.set_game_over(self.mgr)

    def advance_game_state(self, old_state):
        half_play_duration = self.half_play_duration()
        half_time_duration = self.half_time_duration()
        gong_reason = None
        gong_duration = 1000

        if self.mgr.timeoutState() == TimeoutState.white:
            self.timeout_mgr.click(self.mgr, TimeoutState.none)
            gong_reason = "End of White Timeout"
            gong_duration = 1000
        elif self.mgr.timeoutState() == TimeoutState.black:
            self.timeout_mgr.click(self.mgr, TimeoutState.none)
            gong_reason = "End of Black Timeout"
            gong_duration = 1000
        elif old_state == GameState.first_half:
            self.game_break(half_time_duration, GameState.half_time)
            gong_reason = "End of First Half"
            gong_duration = 1000
        elif old_state == GameState.half_time:
            self.timeout_mgr.reset_allowances()
            self.play_ready(half_play_duration, GameState.second_half)
            gong_reason = "End of Half Time"
            gong_duration = 1000
        elif old_state == GameState.second_half:
            self.gong_clicked("End of Second Half", 2500)
            confirm_start = time.time()
            self.confirm_scores()
            confirm_end = time.time()
            if (self.mgr.blackScore() == self.mgr.whiteScore() and self.has_overtime()):
                break_duration = self.pre_overtime_break()
                ref_delay = confirm_end - confirm_start
                break_duraiton = max(0, break_duration - ref_delay)
                self.game_break(break_duration, GameState.pre_ot)
            elif (self.mgr.blackScore() == self.mgr.whiteScore() and self.has_sudden_death()):
                break_duration = self.pre_sudden_death_duration()
                ref_delay = confirm_end - confirm_start
                break_duraiton = max(0, break_duration - ref_delay)
                self.game_break(break_duration, GameState.pre_sudden_death)
            else:
                self.game_over()
        elif old_state == GameState.pre_ot:
            self.play_ready(self.overtime_duration(), GameState.ot_first)
            gong_reason = "End of Pre Overtime Break"
            gong_duration = 1000
        elif old_state == GameState.ot_first:
            self.game_break(self.overtime_break_duration(), GameState.ot_half)
            gong_reason = "End of Overtime First Half"
            gong_duration = 1000
        elif old_state == GameState.ot_half:
            self.play_ready(self.overtime_duration(), GameState.ot_second)
            gong_reason = "End of Overtime Half Time"
            gong_duration = 1000
        elif old_state == GameState.ot_second:
            self.gong_clicked("End of Overtime Second Half", 2500)
            confirm_start = time.time()
            self.confirm_scores()
            confirm_end = time.time()
            if (self.mgr.blackScore() == self.mgr.whiteScore() and self.has_sudden_death()):
                break_duration = self.pre_sudden_death_duration()
                ref_delay = confirm_end - confirm_start
                break_duraiton = max(0, break_duration - ref_delay)
                self.game_break(break_duration, GameState.pre_sudden_death)
            else:
                self.game_over()
        elif old_state == GameState.pre_sudden_death:
            self.play_ready(self.sudden_death_duration(), GameState.sudden_death)
            gong_reason = "End of Pre Sudden Death"
            gong_duration = 1000
        elif old_state == GameState.sudden_death:
            self.gong_clicked("End of Timed Sudden Death", 2500)
            self.game_over()
        elif old_state == GameState.game_over:
            self.timeout_mgr.reset(self.mgr)
            self.mgr.setGameClockRunning(True)
        elif old_state == GameState.pre_game:
            self.gong_clicked("End of Pre Game", 1000)
            self.mgr.setGameClock(half_play_duration)
            self.mgr.setGameState(GameState.first_half)
            self.timeout_mgr.record_game_start()

        if gong_reason is not None:
            self.gong_clicked(gong_reason, gong_duration)

    def refresh_time(self):
        game_clock = self.mgr.gameClock()
        game_mins = game_clock // 60
        game_secs = game_clock % 60
        if self.mgr.gameState() == GameState.game_over:
            game_mins += 3
        self.game_clock_var.set("%02d:%02d" % (game_mins, game_secs))

        if game_clock <= 0 and self.mgr.gameClockRunning():
            self.advance_game_state(self.mgr.gameState())

        if self.mgr.timeoutState() != TimeoutState.none:
            text, color = {
                TimeoutState.ref          : ("REF TIMEOUT",  "#ffff00"),
                TimeoutState.penalty_shot : ("PENALTY SHOT", "#ff0000"),
                TimeoutState.white        : ("WHITE T/O",    "#ffffff"),
                TimeoutState.black        : ("BLACK T/O",    "#0000ff"),
            }[self.mgr.timeoutState()]
        else:
            text, color = {
                GameState.pre_game         : ("NEXT GAME",        "#ffff00"),
                GameState.first_half       : ("FIRST HALF",       "#00ff00"),
                GameState.half_time        : ("HALF TIME",        "#ff8000"),
                GameState.second_half      : ("SECOND HALF",      "#00ff00"),
                GameState.game_over        : ("NEXT GAME",        "#ff0000"),
                GameState.pre_ot           : ("PRE-OVERTIME",     "#ffff00"),
                GameState.ot_first         : ("OVERTIME FIRST",   "#00ff00"),
                GameState.ot_half          : ("OVERTIME HALF",    "#ff8000"),
                GameState.ot_second        : ("OVERTIME SECOND",  "#ffff00"),
                GameState.pre_sudden_death : ("PRE SUDDEN DEATH", "#ffff00"),
                GameState.sudden_death     : ("SUDDEN DEATH",     "#ff0000"),
            }[self.mgr.gameState()]
        self.status_var.set(text)
        self.status_label._inner.config(fg=color)

        refresh_ms = 50
        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

    def gong_clicked(self, reason, duration):
        print("gong clicked -- " + str(time.time()) + " -- " + reason + " -- " + str(duration))
        self.mgr.setGameClockRunning(True)
        self.not_yet_started = False
        self.iomgr.setSound(1)
        self.root.after(duration, lambda: self.iomgr.setSound(0))

    def edit_score(self):
        def set_score(black, white):
            self.mgr.setBlackScore(black)
            self.mgr.setWhiteScore(white)
            self.post_score(False)
            if (self.mgr.gameState() == GameState.sudden_death and
                self.mgr.blackScore() != self.mgr.whiteScore()):
                self.game_over()
        ScoreEditor(self.root, self.tb_offset, "Edit Scores",
                    self.mgr.blackScore(),
                    self.mgr.whiteScore(), set_score, self.cfg)

    def increment_white_score(self):
        def goal(player_no):
            self.mgr.addWhiteGoal(player_no)
            self.post_score(False)
            if (self.mgr.gameState() == GameState.sudden_death and
                self.mgr.blackScore() != self.mgr.whiteScore()):
                self.game_over()
        ScoreIncrementer(self.root, self.tb_offset, False, goal, self.cfg)

    def increment_black_score(self):
        def goal(player_no):
            self.mgr.addBlackGoal(player_no)
            self.post_score(False)
            if (self.mgr.gameState() == GameState.sudden_death and
                self.mgr.blackScore() != self.mgr.whiteScore()):
                self.game_over()
        ScoreIncrementer(self.root, self.tb_offset, True, goal, self.cfg)

    def edit_time(self):
        was_running = self.mgr.gameClockRunning()
        self.mgr.setGameClockRunning(False)
        clock_at_pause = self.mgr.gameClock();

        def submit_clicked(game_clock):
            self.mgr.setGameClock(game_clock)
            self.mgr.setGameClockRunning(was_running)

        def cancel_clicked():
            self.mgr.setGameClockRunning(was_running)

        TimeEditor(self.root, self.tb_offset, clock_at_pause, submit_clicked, cancel_clicked, self.cfg, self.mgr)

    def half_play_duration(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['half_duration']
        return self.cfg.getint('game', 'half_play_duration')

    def half_time_duration(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['half_time_duration']
        return self.cfg.getint('game', 'half_time_duration')

    def team_timeouts_allowed(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['game_timeouts']['allowed']
        return self.cfg.getint('game', 'team_timeouts_allowed')

    def team_timeouts_per_half(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['game_timeouts']['per_half']
        return self.cfg.getboolean('game', 'team_timeouts_per_half')

    def team_timeout_duration(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['game_timeouts']['duration']
        return self.cfg.getint('game', 'team_timeout_duration')

    def has_overtime(self):
        return True
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['overtime_allowed']
        return self.cfg.getboolean('game', 'has_overtime')

    def overtime_duration(self):
        return 5 * 60
        return self.cfg.getint('game', 'ot_half_play_duration')

    def has_sudden_death(self):
        return True
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                return rules['sudden_death_allowed']
        return self.cfg.getboolean('game', 'sudden_death_allowed')

    def sudden_death_duration(self):
        return 99 * 60
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                duration = rules['max_sudden_death_duration']
                if duration:
                    return duration
        return self.cfg.getint('game', 'max_sudden_death_duration')

    def pre_overtime_break(self):
        return 3 * 60
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                try:
                    return rules['pre_overtime_break']
                except Exception:
                    pass
        return self.cfg.getint('game', 'pre_overtime_break')

    def overtime_break_duration(self):
        return 1 * 60
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                try:
                    return rules['overtime_break_duration']
                except Exception:
                    pass
        return self.cfg.getint('game', 'overtime_break_duration')

    def pre_sudden_death_duration(self):
        return 1 * 60
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                try:
                    return rules['pre_sudden_death_duration']
                except Exception:
                    pass
        return self.cfg.getint('game', 'pre_sudden_death_duration')

    def overtime_timeouts_allowed(self):
        if self.game_info:
            rules = self.game_info['timing_rules']
            if rules is not None:
                try:
                    return rules['overtime_timeouts_allowed']
                except Exception:
                    pass
        return self.cfg.getboolean('game', 'overtime_timeouts_allowed')

    def set_game_info(self, game):
        self.game_info = game
        if self.not_yet_started:
            self.mgr.setGameState(GameState.pre_game)
            self.mgr.setGameClock(FIRST_PREGAME_LEN)
