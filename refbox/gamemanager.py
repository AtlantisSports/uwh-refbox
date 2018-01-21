import time
import math

class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3


class TimeoutState(object):
    none = 0
    ref = 1


class TeamColor(object):
    black = 0
    white = 1


def now():
    return math.floor(time.time())

class GameManager(object):

    def __init__(self, observers=None):
        self._white_score = 0
        self._black_score = 0
        self._duration = 0
        self._time_at_start = None
        self._game_state = GameState.first_half
        self._timeout_state = TimeoutState.none
        self._observers = observers or []
        self._penalties = [[],[]]

    def gameClock(self):
        if not self.gameClockRunning():
            return self._duration

        game_clock = self._duration - (now() - self._time_at_start)
        return game_clock

    def setGameClock(self, n):
        self._duration = n

        if self.gameClockRunning():
            self._time_at_start = now()

        for mgr in self._observers:
            mgr.setGameClock(n)

    def whiteScore(self):
        return self._white_score

    def setWhiteScore(self, n):
        self._white_score = n

        for mgr in self._observers:
            mgr.setWhiteScore(n)

    def blackScore(self):
        return self._black_score

    def setBlackScore(self, n):
        self._black_score = n

        for mgr in self._observers:
            mgr.setBlackScore(n)

    def gameClockRunning(self):
        return bool(self._time_at_start)

    def setGameClockRunning(self, b):
        if b == self.gameClockRunning():
            return

        if b:
            print('game clock resumed')
            self._time_at_start = now()
            if self._game_state != GameState.half_time:
                self._start_unstarted_penalties(self.gameClock())
        else:
            print('game clock paused')
            self._duration -= now() - self._time_at_start
            self._time_at_start = None

        for mgr in self._observers:
            mgr.setGameClockRunning(b)

    def gameState(self):
        return self._game_state

    def setGameState(self, state):
        self._game_state = state

        for mgr in self._observers:
            mgr.setGameState(state)

    def timeoutState(self):
        return self._timeout_state

    def setTimeoutState(self, state):
        self._timeout_state = state

        for mgr in self._observers:
            mgr.setTimeoutState(state)

    def gameStateFirstHalf(self):
        return self._game_state == GameState.first_half

    def setGameStateFirstHalf(self):
        self.setGameState(GameState.first_half)

        for mgr in self._observers:
            mgr.setGameStateFirstHalf()

    def gameStateHalfTime(self):
        return self._game_state == GameState.half_time

    def setGameStateHalfTime(self):
        self.setGameState(GameState.half_time)

        for mgr in self._observers:
            mgr.setGameStateHalfTime()

    def gameStateSecondHalf(self):
        return self._game_state == GameState.second_half

    def setGameStateSecondHalf(self):
        self.setGameState(GameState.second_half)

        for mgr in self._observers:
            mgr.setGameStateSecondHalf()

    def gameStateGameOver(self):
        return self._game_state == GameState.game_over

    def setGameStateGameOver(self):
        self.setGameState(GameState.game_over)

        for mgr in self._observers:
            mgr.setGameStateGameOver()

    def timeoutStateNone(self):
        return self._timeout_state == TimeoutState.none

    def setTimeoutStateNone(self):
        self._timeout_state = TimeoutState.none

        for mgr in self._observers:
            mgr.setTimeoutStateNone()

    def timeoutStateRef(self):
        return self._timeout_state == TimeoutState.ref

    def setTimeoutStateRef(self):
        self._timeout_state = TimeoutState.ref
        for mgr in self._observers:
            mgr.setTimeoutStateRef()

    def addPenalty(self, p):
        self._penalties[p.team()].append(p)
        if self.gameClockRunning():
            p.setStartTime(self.gameClock())

    def delPenalty(self, p):
        if p in self._penalties[p.team()]:
            self._penalties[p.team()].remove(p)

    def penalties(self, team_color):
        return self._penalties[team_color]

    def deleteAllPenalties(self):
        self._penalties = [[],[]]

    def _start_unstarted_penalties(self, game_clock):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.startTime():
                p.setStartTime(game_clock)

    def pauseOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(0):
                p._duration_remaining = p.timeRemaining(0)
                p._start_time = None

    def restartOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(0):
                p._start_time = self._duration


class Penalty(object):

    def __init__(self, player, team, duration, start_time = None):
        self._player = player
        self._team = team

        # Game time when the penalty started
        self._start_time = start_time

        # Total time of the penalty
        self._duration = duration

        # Amount left to be served (might be less than duration if partially
        # served in the first half)
        self._duration_remaining = duration

    def setStartTime(self, start_time):
        self._start_time = start_time

    def startTime(self):
        return self._start_time

    def timeRemaining(self, game_clock):
        if not self._start_time:
            return self._duration_remaining
        remaining = self._duration_remaining - (self._start_time - game_clock)
        return max(remaining, 0)

    def servedCompletely(self, game_clock):
        return self.timeRemaining(game_clock) <= 0

    def player(self):
        return self._player

    def setPlayer(self, player):
        self._player = player

    def team(self):
        return self._team

    def duration(self):
        return self._duration

    def setDuration(self, duration):
        self._duration = duration
        self._duration_remaining = duration

    def dismissed(self):
        return self._duration == -1
