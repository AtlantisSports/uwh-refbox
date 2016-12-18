try:
    import Tkinter as tk
    import ttk
except ImportError:
    import tkinter as tk
    from tkinter import ttk

import time

_font_name = 'Consolas'


def sized_frame(master, height, width):
    F = tk.Frame(master, height=height, width=width)
    F.pack_propagate(0)  # Don't shrink
    F.pack()
    return F


def SizedLabel(root, var, bg, fg, font, height, width):
    sf = sized_frame(root, height, width)
    l = tk.Label(sf, textvariable=var, bg=bg, fg=fg, font=font)
    l.pack(fill=tk.BOTH, expand=1)
    return sf


def SizedButton(root, callback, text, bg, fg, font, height, width):
    style = ttk.Style()
    style.configure("Sized.TButton", foreground=fg, background=bg, highlightthickness=4,
                    highlightbackground="dark grey", activebackground=bg, font=font, relief='flat')

    sf = sized_frame(root, height, width)
    b = ttk.Button(sf, text=text, command=callback, style="Sized.TButton")
    b.pack(fill=tk.BOTH, expand=1)
    return sf


def ConfirmManualEditScore(master, tb_offset, cancel_continuation, manual_continuation):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 310, 0, 170 + tb_offset))

    def manual_edit_clicked():
        root.destroy()
        manual_continuation()

    def cancel_clicked():
        root.destroy()
        cancel_continuation()

    root.overrideredirect(1)
    root.transient(master)

    manual_edit_button = SizedButton(root, manual_edit_clicked,
                                     "MANUALLY EDIT SCORE", "orange", "black", (
                                         _font_name, 50),
                                     180, 800)
    manual_edit_button.grid(row=0, column=0)

    cancel_button = SizedButton(root, cancel_clicked,
                                "CANCEL", "red", "black", (_font_name, 36),
                                130, 800)
    cancel_button.grid(row=1, column=0)

    root.mainloop()


def ManualEditScore(master, tb_offset, white_score, black_score,
                    cancel_continuation, submit_continuation):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 310, 0, 170 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    white_new_var = tk.IntVar(value=white_score)
    black_new_var = tk.IntVar(value=black_score)

    button_font = (_font_name, 36)
    label_font = (_font_name, 96)

    def white_up():
        white_new_var.set(white_new_var.get() + 1)

    def white_dn():
        white_new_var.set(white_new_var.get() - 1)

    def black_up():
        black_new_var.set(black_new_var.get() + 1)

    def black_dn():
        black_new_var.set(black_new_var.get() - 1)

    def cancel_clicked():
        root.destroy()
        cancel_continuation()

    def submit_clicked():
        root.destroy()
        submit_continuation(white_new_var.get(), black_new_var.get())

    cancel_button = SizedButton(root, cancel_clicked,
                                "CANCEL", "red", "black", button_font,
                                130, 400)
    cancel_button.grid(row=2, column=0, columnspan=2)

    submit_button = SizedButton(root, submit_clicked,
                                "SUBMIT", "green", "black", button_font,
                                130, 400)
    submit_button.grid(row=2, column=2, columnspan=2)

    white_new = SizedLabel(root, white_new_var, "black", "white", label_font,
                           160, 300)
    white_new.grid(row=0, rowspan=2, column=1)

    black_new = SizedLabel(root, black_new_var, "black", "blue", label_font,
                           160, 300)
    black_new.grid(row=0, rowspan=2, column=2)

    white_up_button = SizedButton(root, white_up,
                                  "+", "light blue", "black", button_font,
                                  80, 100)
    white_up_button.grid(row=0, column=0)

    white_dn_button = SizedButton(root, white_dn,
                                  "-", "grey", "black", button_font,
                                  80, 100)
    white_dn_button.grid(row=1, column=0)

    black_up_button = SizedButton(root, black_up,
                                  "+", "light blue", "black", button_font,
                                  80, 100)
    black_up_button.grid(row=0, column=3)

    black_dn_button = SizedButton(root, black_dn,
                                  "-", "grey", "black", button_font,
                                  80, 100)
    black_dn_button.grid(row=1, column=3)


def ConfirmRefTimeOut(master, tb_offset, game_clock, edit_continuation,
                      resume_continuation):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 190, 0, 115 + 170 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    def resume_clicked():
        root.destroy()
        resume_continuation(game_clock)

    def edit_clicked():
        root.destroy()
        edit_continuation()

    resume_button = SizedButton(root, resume_clicked,
                                "RESUME\nPLAY", "green", "black", (
                                    _font_name, 50),
                                190, 400)
    resume_button.grid(row=0, column=0)

    edit_button = SizedButton(root, edit_clicked,
                              "EDIT TIME", "orange", "black", (_font_name, 50),
                              190, 400)
    edit_button.grid(row=0, column=1)

    root.mainloop()


def ManualEditTime(master, tb_offset, clock_at_pause,
                   cancel_continuation, submit_continuation):
    root = tk.Toplevel(master)
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.geometry('{}x{}+{}+{}'.format(800, 310, 0, 170 + tb_offset))

    root.overrideredirect(1)
    root.transient(master)

    clock_at_pause_var = tk.IntVar(value=clock_at_pause)

    button_font = (_font_name, 36)
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
        cancel_continuation(clock_at_pause)

    def submit_clicked():
        root.destroy()
        submit_continuation(clock_at_pause_var.get())

    cancel_button = SizedButton(root, cancel_clicked,
                                "CANCEL", "red", "black", button_font,
                                150, 400)
    cancel_button.grid(row=2, column=0, columnspan=2)

    submit_button = SizedButton(root, submit_clicked,
                                "SUBMIT", "green", "black", button_font,
                                150, 400)
    submit_button.grid(row=2, column=2, columnspan=2)

    m_up_button = SizedButton(root, game_clock_m_up,
                              u"Min \u2191", "light blue", "black", button_font,
                              80, 200)
    m_up_button.grid(row=0, column=0)

    m_dn_button = SizedButton(root, game_clock_m_dn,
                              u"Min \u2193", "grey", "black", button_font,
                              80, 200)
    m_dn_button.grid(row=1, column=0)

    s_up_button = SizedButton(root, game_clock_s_up,
                              u"Sec \u2191", "light blue", "black", button_font,
                              80, 200)
    s_up_button.grid(row=0, column=3)

    s_dn_button = SizedButton(root, game_clock_s_dn,
                              u"Sec \u2193", "grey", "black", button_font,
                              80, 200)
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

    button_font = label_font
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
                         team_color.upper() + "\nSCORE", "dark cyan", "black",
                         button_font, button_height, button_width)
    button.grid(row=2, column=column)

    penalty = tk.Frame(root, height=penalty_height, width=penalty_width,
                       bg="black")
    penalty.grid(row=3, column=column)

    return root


class NormalView(object):

    def __init__(self, mgr, iomgr, NO_TITLE_BAR):
        self.mgr = mgr
        self.iomgr = iomgr
        self.first_game_started = False

        self.root = tk.Tk()
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.geometry('{}x{}+{}+{}'.format(800, 480, 0, 0))
        if NO_TITLE_BAR:
            self.root.overrideredirect(1)
            self.tb_offset = 0
        else:
            self.tb_offset = 70

        refresh_ms = 50

        ScoreColumn(self.root, 0, 'white', 'white',
                    refresh_ms, lambda: self.mgr.whiteScore(),
                    lambda: self.score_change_clicked())
        self.center_column(refresh_ms)
        ScoreColumn(self.root, 2, 'black', 'blue',
                    refresh_ms, lambda: self.mgr.blackScore(),
                    lambda: self.score_change_clicked())

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

        gong_font = status_font
        gong_height = 120
        gong_width = clock_width

        ref_signal_height = 190
        ref_signal_width = clock_width

        time_change_font = gong_font
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
                                  "red", "black", gong_font, gong_height,
                                  gong_width)
        gong_button.grid(row=2, column=1)

        time_button = SizedButton(self.root, lambda: self.ref_timeout_clicked(),
                                  "REF TIMEOUT", "yellow", "black", time_change_font,
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
            self.mgr.setGameClockRunning(False)
            if self.mgr.gameStateFirstHalf():
                self.mgr.setGameStateHalfTime()
                # FIXME:
                # self.mgr.setGameClock(HALF_TIME_DURATION)
                self.gong_clicked()
                self.mgr.setGameClockRunning(True)
                self.root.update()
            elif self.mgr.gameStateHalfTime():
                self.mgr.setGameStateSecondHalf()
                # FIXME:
                # self.mgr.setGameClock(HALF_PLAY_DURATION)
                self.gong_clicked()
                self.mgr.setGameClockRunning(True)
                self.root.update()
            elif self.mgr.gameStateSecondHalf():
                self.mgr.setGameStateGameOver()
                # FIXME:
                # self.mgr.setGameClock(GAME_OVER_DURATION)
                self.gong_clicked()
                self.mgr.setGameClockRunning(True)
                self.root.update()
            elif self.mgr.gameStateGameOver():
                self.mgr.setBlackScore(0)
                self.mgr.setWhiteScore(0)
                self.mgr.setGameStateFirstHalf()
                # FIXME:
                # self.mgr.setGameClock(HALF_PLAY_DURATION)
                self.gong_clicked()
                self.mgr.setGameClockRunning(True)

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
        self.root.update()

        refresh_ms = 50
        self.game_clock_label.after(refresh_ms, lambda: self.refresh_time())

    def gong_clicked(self):
        print("gong clicked")
        if not self.first_game_started:
            self.first_game_started = True
            self.mgr.setGameClockRunning(True)
        self.iomgr.setSound(1)
        time.sleep(1)
        self.iomgr.setSound(0)

    def score_change_clicked(self):
        def manual_continuation():
            def submit_clicked(white_score, black_score):
                self.mgr.setWhiteScore(white_score)
                self.mgr.setBlackScore(black_score)

            ManualEditScore(self.root, self.tb_offset,
                            self.mgr.whiteScore(), self.mgr.blackScore(),
                            lambda: None, submit_clicked)

        ConfirmManualEditScore(self.root,
                               self.tb_offset,
                               lambda: None,
                               manual_continuation)

    def ref_timeout_clicked(self, save_state=True):
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

        if save_state:
            self.state_before_pause = self.mgr.gameState()
            self.mgr.setTimeoutStateRef()

        self.refresh_time()

        def edit_continuation(self):
            def submit_clicked(game_clock):
                self.mgr.setGameClock(max(game_clock, 0))
                self.ref_timeout_clicked(save_state=False)

            def cancel_clicked(game_clock):
                self.mgr.setGameClock(max(clock_at_pause, 0))
                self.ref_timeout_clicked(save_state=False)

            ManualEditTime(self.root, self.tb_offset, clock_at_pause,
                           cancel_clicked, submit_clicked)

        def resume_continuation(self, pause_time):
            self.mgr.setGameState(self.state_before_pause)
            self.mgr.setTimeoutStateNone()
            self.mgr.setGameClockRunning(True)
            self.mgr.setGameClock(max(pause_time, 0))

        ConfirmRefTimeOut(self.root,
                          self.tb_offset,
                          clock_at_pause,
                          lambda: edit_continuation(self),
                          lambda pause_time: resume_continuation(self, pause_time))
