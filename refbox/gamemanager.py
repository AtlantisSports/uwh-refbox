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

    def gameClock(self):
        if not self.gameClockRunning():
            return self._duration

        return self._duration - (now() - self._time_at_start)

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
        self._game_state = GameState.first_half

        for mgr in self._observers:
            mgr.setGameStateFirstHalf()

    def gameStateHalfTime(self):
        return self._game_state == GameState.half_time

    def setGameStateHalfTime(self):
        self._game_state = GameState.half_time

        for mgr in self._observers:
            mgr.setGameStateHalfTime()

    def gameStateSecondHalf(self):
        return self._game_state == GameState.second_half

    def setGameStateSecondHalf(self):
        self._game_state = GameState.second_half

        for mgr in self._observers:
            mgr.setGameStateSecondHalf()

    def gameStateGameOver(self):
        return self._game_state == GameState.game_over

    def setGameStateGameOver(self):
        self._game_state = GameState.game_over

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
