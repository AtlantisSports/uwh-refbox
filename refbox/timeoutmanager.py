from uwh.gamemanager import TimeoutState, GameState, TeamColor
import time

class TimeoutManager(object):
    def __init__(self, var, team_timeout_duration):
        var.set("START")
        self._text = var
        self._team_timeout_duration = team_timeout_duration
        self._timeout_running = False
        self._reset_handlers = []
        self._total_delay = 0
        self.reset_allowances()

    def reset_allowances(self):
        self._timeout_allowed = { TeamColor.black : True,
                                  TeamColor.white : True }

    def timeout_allowed(self, team):
        return self._timeout_allowed[team]

    def timeout_used(self, team):
        self._timeout_allowed[team] = False

    def ready_to_start(self):
        return self._text.get() == "START"

    def ready_to_reset(self):
        return self._text.get() == "RESET"

    def ready_to_resume(self):
        return self._text.get() == "RESUME"

    def set_game_over(self, mgr):
        actual_duration = time.time() - self._game_start_time
        print("actual duration:     " + str(actual_duration))

        expected_duration = (15 + 3 + 15) * 60
        print("expected duration:   " + str(expected_duration))

        diff = (actual_duration - expected_duration)
        print("difference:          " + str(diff))

        amount_over = max(0, diff)
        print("over by:             " + str(amount_over))

        print("total delay was:     " + str(self._total_delay))
        self._total_delay += amount_over

        pre_game_duration = 3 * 60
        nominal_break = 15 * 60 - pre_game_duration
        minimum_break = 4 * 60 - pre_game_duration

        if nominal_break - self._total_delay < minimum_break:
            # Amount of time to be recovered is big, so all we can recover is
            # limited by the minimum break duration.
            break_duration = minimum_break
            self._total_delay -= nominal_break - break_duration
        else:
            # Amount of time to be recovered is small enough to entirely
            # recover within this break.
            break_duration = nominal_break - self._total_delay
            self._total_delay = 0
        print("total delay will be: " + str(self._total_delay))

        self._text.set("RESET")
        mgr.setGameState(GameState.game_over)
        mgr.setGameClockRunning(False)
        mgr.setGameClock(break_duration)
        mgr.deleteAllPenalties()
        mgr.delAllGoals()

        mgr.setGameClockRunning(True)

    def add_reset_handler(self, callback):
        self._reset_handlers += [callback]

    def reset(self, mgr):
        self.reset_allowances()
        mgr.setBlackScore(0)
        mgr.setWhiteScore(0)
        mgr.setGameState(GameState.pre_game)
        mgr.setGameClockRunning(False)
        mgr.setGameClock(3 * 60)
        mgr.deleteAllPenalties()
        mgr.delAllGoals()
        for handler in self._reset_handlers:
            handler()
        self._text.set("START")

    def set_ready(self, mgr):
        self._timeout_running = False
        self._text.set("RESUME")

    def record_game_start(self):
        self._game_start_time = time.time()
        print("game start was: " + str(self._game_start_time))

    def click(self, mgr, state):
        if self.ready_to_start():
            self._game_start_time = time.time()

        if mgr.gameState() == GameState.game_over:
            self.reset(mgr)
            return

        if (state == TimeoutState.white or
            state == TimeoutState.black):
            self._timeout_allowed[state] = False

        if mgr.timeoutState() == TimeoutState.none and state != TimeoutState.none:
            self._timeout_running = True
            mgr.setGameClockAtPause(mgr.gameClock())
            mgr.pauseOutstandingPenalties()
            mgr.setGameClockRunning(False)
            mgr.setTimeoutState(state)
            if (state == TimeoutState.white or
                state == TimeoutState.black):
                mgr.setGameClock(self._team_timeout_duration())
                mgr.setGameClockRunning(True)
            self._text.set('RESUME')
            return

        mgr.setGameClockRunning(True)
        if self._timeout_running:
            mgr.setGameClock(mgr.gameClockAtPause())
            self._timeout_running = False
        mgr.restartOutstandingPenalties()
        mgr.setTimeoutState(TimeoutState.none)
        self._text.set('TIMEOUT')
