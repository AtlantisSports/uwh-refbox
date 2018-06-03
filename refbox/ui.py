import tkinter as tk
from tkinter import ttk
from configparser import ConfigParser
import os
from .timeoutmanager import TimeoutManager
from uwh.gamemanager import GameManager, TeamColor, Penalty, TimeoutState
from functools import partial

_font_name = 'Consolas'

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

        # game
        'half_play_duration': '600',
        'half_time_duration': '180',
        'team_timeout_duration': '60',
        'pool' : '1',
        'tid' : '16',
        'uwhscores_url' : 'http://localhost:5000/api/v1',
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
    def __init__(self, master, tb_offset, clock_at_pause, on_submit, on_cancel, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                           cfg.getint('hardware', 'screen_y'),
                                           0, 0))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit
        self.on_cancel = on_cancel

        space = tk.Frame(self.root, height=50, width=100, bg="black")
        space.grid(row=0, column=0)

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
        if x > 0:
            self.clock_at_pause_var.set(x - 1)

    def game_clock_m_up(self):
        x = self.clock_at_pause_var.get()
        self.clock_at_pause_var.set(x + 60)

    def game_clock_m_dn(self):
        x = self.clock_at_pause_var.get()
        if x - 60 >= 0:
            self.clock_at_pause_var.set(x - 60)
        else:
            self.clock_at_pause_var.set(0)

    def cancel_clicked(self):
        self.root.destroy()
        self.on_cancel()

    def submit_clicked(self):
        self.root.destroy()
        self.on_submit(self.clock_at_pause_var.get())


class ScoreEditor(object):
    def __init__(self, master, tb_offset, score, is_black, on_submit, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                           cfg.getint('hardware', 'screen_y'),
                                           0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit

        header_font = (_font_name, 36)
        header_text = "BLACK" if is_black else "WHITE"
        header = SizedLabel(self.root, header_text, "black", "white", header_font, 50, 200)
        header.grid(row=0, columnspan=2, column=3)

        self.score_var = tk.IntVar(value=score)
        score_height = 120

        dn_button = SizedButton(self.root, self.dn, "-", "LightBlue.TButton", score_height, 100)
        dn_button.grid(row=1, column=2)

        label_font = (_font_name, 96)
        label = SizedLabel(self.root, self.score_var, "black", "white", label_font, score_height, 200)
        label.grid(row=1, column=3, columnspan=2)

        up_button = SizedButton(self.root, self.up, "+", "LightBlue.TButton", score_height, 100)
        up_button.grid(row=1, column=5)

        cancel_button = SizedButton(self.root, self.cancel_clicked, "CANCEL", "Red.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        cancel_button.grid(row=2, column=0, columnspan=4)

        submit_button = SizedButton(self.root, self.submit_clicked, "SUBMIT", "Green.TButton",
                                    150, cfg.getint('hardware', 'screen_x') / 2)
        submit_button.grid(row=2, column=4, columnspan=4)

    def up(self):
        x = self.score_var.get()
        if x < 99:
            self.score_var.set(x + 1)

    def dn(self):
        x = self.score_var.get()
        if x > 0:
            self.score_var.set(x - 1)

    def cancel_clicked(self):
        self.root.destroy()

    def submit_clicked(self):
        self.root.destroy()
        self.on_submit(self.score_var.get())


class ConfirmDialog(object):
    #FIXME: merge this with the ScoreIncrementer

    def __init__(self, master, tb_offset, prompt, on_yes, on_no, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_yes = on_yes
        self.on_no = on_no

        space = tk.Frame(self.root, height=100, width=100, bg="black")
        space.grid(row=0, column=0)

        header_font = (_font_name, 20)
        header = SizedLabel(self.root, prompt, "black", "white", header_font,
                            50, cfg.getint('hardware', 'screen_x'))
        header.grid(row=1, columnspan=2, column=0)

        no_button = SizedButton(self.root, self.no_clicked, "NO", "Red.TButton",
                                150, cfg.getint('hardware', 'screen_x') / 2)
        no_button.grid(row=2, column=0)

        yes_button = SizedButton(self.root, self.yes_clicked, "YES", "Green.TButton",
                                 150, cfg.getint('hardware', 'screen_x') / 2)
        yes_button.grid(row=2, column=1)

    def no_clicked(self):
        self.root.destroy()
        self.on_no()

    def yes_clicked(self):
        self.root.destroy()
        self.on_yes()


class ScoreIncrementer(object):
    def __init__(self, master, tb_offset, score, is_black, on_submit, cfg):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_submit = on_submit
        self.score = score

        space = tk.Frame(self.root, height=100, width=100, bg="black")
        space.grid(row=0, column=0)

        header_font = (_font_name, 36)
        color = "BLACK" if is_black else "WHITE"
        header_text = "SCORE {}?".format(color)
        header = SizedLabel(self.root, header_text, "black", "white", header_font,
                            50, cfg.getint('hardware', 'screen_x')/ 2)
        header.grid(row=1, columnspan=2, column=0)

        no_button = SizedButton(self.root, self.no_clicked, "NO", "Red.TButton",
                                150, cfg.getint('hardware', 'screen_x') / 2)
        no_button.grid(row=2, column=0)

        yes_button = SizedButton(self.root, self.yes_clicked, "YES", "Green.TButton",
                                 150, cfg.getint('hardware', 'screen_x') / 2)
        yes_button.grid(row=2, column=1)

    def no_clicked(self):
        self.root.destroy()

    def yes_clicked(self):
        self.root.destroy()
        if self.score < 99:
            self.on_submit(self.score + 1)


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

        self.outer = sized_frame(root, 250, self.col_width)
        self.outer.grid(row=3, column=col)

        self.canvas = tk.Canvas(self.outer, background="#cccccc")
        self.canvas.pack(side=tk.RIGHT)

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
    def __init__(self, root, tb_offset, height, width, mgr, cfg, uwhscores):
        self.root = root
        self.tb_offset = tb_offset
        self.mgr = mgr
        self.cfg = cfg
        self.uwhscores = uwhscores

        self.games = []

        tid = cfg.get('game', 'tid')
        pool = cfg.get('game', 'pool')

        self.outer = sized_frame(root, height, width)
        self.outer.grid(row=3, column=1, rowspan=2)

        scrollbar = tk.Scrollbar(self.outer, width=30)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.outer, font=(_font_name, 18),
                                  selectmode=tk.SINGLE)
        self.listbox.pack(expand=1, fill=tk.BOTH)
        self.cur_selection = None

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        def response(games):
            self.games = [g for g in games if g['pool'] == pool]

            for game in self.games:
                self.listbox.insert(tk.END, self.desc(game))

            if len(self.games) > 0:
                self.select(0)

            self.outer.after(250, self.poll)

        self.uwhscores.get_game_list(tid, response)

    def desc(self, game):
        return "#{} {} - {} vs {}".format(game['game_type'], game['gid'],
                                          game['white'], game['black'])

    def select(self, idx):
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.cur_selection = (idx,)
        self.mgr.setGid(self.games[idx]['gid'])

    def poll(self):
        now = self.listbox.curselection()
        if now != self.cur_selection:
            temp = self.cur_selection
            self.cur_selection = now

            def on_yes():
                self.select(now[0])
            def on_no():
                self.select(temp[0])

            ConfirmDialog(self.root, self.tb_offset,
                          "Switch to {}?".format(self.desc(self.games[now[0]])),
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
                 penalty=None):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

        self.on_delete = on_delete
        self.on_submit = on_submit

        if team_color == TeamColor.white:
            title_str = "White Penalty"
        else:
            title_str = "Black Penalty"
        label_font = (_font_name, 48)
        title = SizedLabel(self.root, title_str, "black", "white", label_font,
                           height=100, width=cfg.getint('hardware', 'screen_y'))
        title.grid(row=0, column=0, columnspan=2)

        self._penalty = penalty or Penalty('', team_color, 60)
        self._duration = tk.IntVar()
        self._duration.set(self._penalty.duration())

        # Player Selection
        self._numpad = PlayerSelectNumpad(self.root, self._penalty.player())
        self._numpad.grid(row=1, column=0)

        frame_height = 75 * 5
        frame_width = 300

        # Penalty Duration
        time_frame = tk.Frame(self.root, height=frame_height, width=frame_width,
                              bg="grey")
        time_frame.grid(row=1, column=1)
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
        space.grid(row=2, column=0, columnspan=2)

        frame_height = 100
        frame_width = cfg.getint('hardware', 'screen_x')

        # Actions
        submit_frame = tk.Frame(self.root, height=frame_height, width=frame_width,
                                bg="dark grey")
        submit_frame.grid(row=3, column=0, columnspan=2)

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
        self._one_min.config(relief=tk.RAISED, border=4)
        self._two_min.config(relief=tk.RAISED, border=4)
        self._five_min.config(relief=tk.RAISED, border=4)
        self._dismissal.config(relief=tk.RAISED, border=4)
        if kind == 60:
            self._one_min.config(relief=tk.SUNKEN)
        elif kind == 120:
            self._two_min.config(relief=tk.SUNKEN)
        elif kind == 300:
            self._five_min.config(relief=tk.SUNKEN)
        elif kind == -1:
            self._dismissal.config(relief=tk.SUNKEN)
        self._duration.set(kind)

    def cancel_clicked(self):
        self.root.destroy()

    def delete_clicked(self):
        self.root.destroy()
        self.on_delete(self._penalty)

    def submit_clicked(self):
        self.root.destroy()
        self.on_submit(self._numpad.get_value(), self._duration.get())


class TimeoutEditor(object):
    def __init__(self, master, tb_offset, mgr, cfg, on_ref, on_white, on_black, on_shot):
        self.root = tk.Toplevel(master, background='black')
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(cfg.getint('hardware', 'screen_x'),
                                                cfg.getint('hardware', 'screen_y'),
                                                0, tb_offset))

        maybe_hide_cursor(self.root)

        self.root.overrideredirect(1)
        self.root.transient(master)

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
        ref = SizedButton(submit_frame, self.ref_clicked, "Ref Timeout",
                             "Yellow.TButton", frame_height / 5, frame_width / 2)
        ref.grid(row=0, column=0)

        white = SizedButton(submit_frame, self.white_clicked,
                            "White Timeout", "White.TButton",
                            frame_height / 5, frame_width / 2)
        white.grid(row=1, column=0)

        black = SizedButton(submit_frame, self.black_clicked,
                            "Black Timeout", "Blue.TButton",
                            frame_height / 5, frame_width / 2)
        black.grid(row=2, column=0)

        shot = SizedButton(submit_frame, self.shot_clicked, "Penalty Shot",
                             "Cyan.TButton", frame_height / 5, frame_width / 2)
        shot.grid(row=3, column=0)

        cancel = SizedButton(submit_frame, self.cancel_clicked, "Cancel",
                             "Red.TButton", frame_height / 5, frame_width / 2)
        cancel.grid(row=4, column=0)

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
        self.mgr.setGameStatePreGame()
        self.mgr.setGameClock(self.cfg.getint('game', 'half_play_duration'))
        self.uwhscores = uwhscores


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
                    lambda: self.edit_white_score(),
                    lambda: self.increment_white_score(),
                    self.cfg)

        self.center_column(refresh_ms)
        ScoreColumn(self.root, 2, 'black', 'blue',
                    refresh_ms, lambda: self.mgr.blackScore(),
                    lambda: self.edit_black_score(),
                    lambda: self.increment_black_score(),
                    self.cfg)

        def poll_clicker(self):
            if self.iomgr.readClicker():
                print("remote clicked")
            else:
                self.iomgr.setSound(0)
            self.root.after(refresh_ms, lambda: poll_clicker(self))
        self.root.after(refresh_ms, lambda: poll_clicker(self))

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
        self.penalties[TeamColor.white].redraw()
        self.penalties[TeamColor.black].redraw()

    def edit_penalty(self, team_color, p):
        def submit_clicked(player, duration):
            p.setPlayer(player)
            p.setDuration(duration)
            self.penalties[team_color].redraw()
        def delete_clicked(penalty):
            self.mgr.delPenalty(penalty)
            self.penalties[team_color].redraw()
        PenaltyEditor(self.root, self.tb_offset, self.mgr, self.cfg, team_color,
                      delete_clicked, submit_clicked, p)

    def add_penalty(self, team_color):
        def submit_clicked(self, player, duration):
            p = Penalty(player, team_color, duration)
            self.mgr.addPenalty(p)
            self.penalties[team_color].redraw()
        PenaltyEditor(self.root, self.tb_offset, self.mgr, self.cfg, team_color,
                      lambda x: None, partial(submit_clicked, self))

    def timeout_clicked(self):
        half_play_duration = self.cfg.getint('game', 'half_play_duration')
        def ref_clicked():
            self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.ref)
            self.redraw_penalties()
        def shot_clicked():
            self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.penalty_shot)
            self.redraw_penalties()
        def white_clicked():
            self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.white)
            self.redraw_penalties()
        def black_clicked():
            self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.black)
            self.redraw_penalties()
        if self.timeout_mgr.ready_to_start() or self.timeout_mgr.ready_to_resume():
            self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.none)
            self.redraw_penalties()
        else:
            TimeoutEditor(self.root, self.tb_offset, self.mgr, self.cfg,
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

        self.game_clock_var = tk.StringVar()
        self.game_clock_var.set("##:##")
        self.game_clock_label = SizedButton(self.root, lambda: self.edit_time(),
                                            self.game_clock_var, "Huge.Neon.TButton",
                                            clock_height, clock_width)
        self.game_clock_label.grid(row=1, column=1)

        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

        time_button_var = tk.StringVar()
        self.timeout_mgr = TimeoutManager(time_button_var, self.cfg.getint('game', 'team_timeout_duration'))
        time_button = SizedButton(self.root,
                                  lambda: self.timeout_clicked(),
                                  time_button_var, "Yellow.TButton",
                                  150, clock_width)
        time_button.grid(row=2, column=1)

        self.settings_view = SettingsView(self.root, self.tb_offset, 400, clock_width,
                                          self.mgr, self.cfg, self.uwhscores)
        self.timeout_mgr.add_reset_handler(self.settings_view.next_game)

    def refresh_time(self):
        game_clock = self.mgr.gameClock()
        game_mins = game_clock // 60
        game_secs = game_clock % 60
        self.game_clock_var.set("%02d:%02d" % (game_mins, game_secs))

        half_play_duration = self.cfg.getint('game', 'half_play_duration')
        half_time_duration = self.cfg.getint('game', 'half_time_duration')

        if game_clock <= 0 and self.mgr.gameClockRunning():
            if self.mgr.timeoutStateWhite():
                self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.none)
            elif self.mgr.timeoutStateBlack():
                self.timeout_mgr.click(self.mgr, half_play_duration, TimeoutState.none)
            elif self.mgr.gameStateFirstHalf():
                self.mgr.deleteServedPenalties()
                self.mgr.pauseOutstandingPenalties()
                self.redraw_penalties()
                self.mgr.setGameStateHalfTime()
                self.mgr.setGameClock(half_time_duration)
                self.gong_clicked()
            elif self.mgr.gameStateHalfTime():
                self.mgr.setGameStateSecondHalf()
                self.mgr.setGameClock(half_play_duration)
                self.mgr.restartOutstandingPenalties()
                self.mgr.deleteServedPenalties()
                self.redraw_penalties()
                self.gong_clicked()
            elif self.mgr.gameStateSecondHalf():
                self.gong_clicked()
                self.mgr.pauseOutstandingPenalties()
                self.mgr.deleteAllPenalties()
                self.redraw_penalties()
                self.timeout_mgr.set_game_over(self.mgr)

        if self.mgr.timeoutStateRef():
            self.status_var.set("REF TIMEOUT")
        elif self.mgr.timeoutStatePenaltyShot():
            self.status_var.set("PENALTY SHOT")
        elif self.mgr.timeoutStateWhite():
            self.status_var.set("WHITE T/O")
        elif self.mgr.timeoutStateBlack():
            self.status_var.set("BLACK T/O")
        elif self.mgr.gameStatePreGame():
            self.status_var.set("PRE GAME")
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
        ScoreEditor(self.root, self.tb_offset, self.mgr.whiteScore(),
                    False, lambda x: self.mgr.setWhiteScore(x), self.cfg)

    def edit_black_score(self):
        ScoreEditor(self.root, self.tb_offset, self.mgr.blackScore(),
                    True, lambda x: self.mgr.setBlackScore(x), self.cfg)

    def increment_white_score(self):
        ScoreIncrementer(self.root, self.tb_offset, self.mgr.whiteScore(),
                         False, lambda x: self.mgr.setWhiteScore(x), self.cfg)

    def increment_black_score(self):
        ScoreIncrementer(self.root, self.tb_offset, self.mgr.blackScore(),
                         True, lambda x: self.mgr.setBlackScore(x), self.cfg)

    def edit_time(self):
        was_running = self.mgr.gameClockRunning()
        self.mgr.setGameClockRunning(False)
        clock_at_pause = self.mgr.gameClock();

        def submit_clicked(game_clock):
            self.mgr.setGameClock(game_clock)
            self.mgr.setGameClockRunning(was_running)

        def cancel_clicked():
            self.mgr.setGameClockRunning(was_running)

        TimeEditor(self.root, self.tb_offset, clock_at_pause, submit_clicked, cancel_clicked, self.cfg)

