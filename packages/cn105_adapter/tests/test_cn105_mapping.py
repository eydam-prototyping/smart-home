import unittest
import cn105_adapter

class TestHttpServer(unittest.TestCase):
    def test_rawToPhys_powerMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.powerMapping, 0) == "OFF")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.powerMapping, 1) == "ON")

    def test_rawToPhys_modeMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.modeMapping, 1) == "HEAT")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.modeMapping, 2) == "DRY")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.modeMapping, 3) == "COOL")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.modeMapping, 7) == "FAN")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.modeMapping, 8) == "AUTO")

    def test_rawToPhys_tempSetMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempSetMapping,  0) == 31)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempSetMapping,  8) == 23)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempSetMapping, 11) == 20)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempSetMapping, 15) == 16)

    def test_rawToPhys_tempRoomMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempRoomMapping,  0) == 10)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempRoomMapping,  8) == 18)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempRoomMapping, 11) == 21)
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.tempRoomMapping, 15) == 25)

    def test_rawToPhys_fanMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.fanMapping, 0) == "AUTO")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.fanMapping, 1) == "QUIET")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.fanMapping, 3) == "2")

    def test_rawToPhys_vaneMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.vaneMapping, 0) == "AUTO")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.vaneMapping, 3) == "3")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.vaneMapping, 7) == "SWING")

    def test_rawToPhys_dirMapping(self):
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.dirMapping,  0) == "NA")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.dirMapping,  3) == "|")
        self.assertTrue(cn105_adapter.rawToPhys(cn105_adapter.dirMapping, 12) == "SWING")

    def test_rawToPhys_powerMapping(self):
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.powerMapping, "off") == 0)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.powerMapping, "Off") == 0)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.powerMapping, "OFF") == 0)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.powerMapping, "ON") == 1)

    def test_rawToPhys_modeMapping(self):
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.modeMapping, "HEAT") == 1)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.modeMapping, "DRY") == 2)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.modeMapping, "COOL") == 3)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.modeMapping, "FAN") == 7)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.modeMapping, "AUTO") == 8)

    def test_rawToPhys_tempSetMapping(self):
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempSetMapping, 31) == 0)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempSetMapping, 23) == 8)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempSetMapping, 20) == 11)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempSetMapping, 16) == 15)

    def test_rawToPhys_tempRoomMapping(self):
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempRoomMapping, 10) == 0)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempRoomMapping, 18) == 8)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempRoomMapping, 21) == 11)
        self.assertTrue(cn105_adapter.physToRaw(cn105_adapter.tempRoomMapping, 25) == 15)