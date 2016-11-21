from .noiomanager import IOManager


def test_iomanager():
    io_mgr = IOManager()
    io_mgr.turnOnWetDisplays()
    io_mgr.setSound(0)
    assert io_mgr.readClicker() is False
