import unittest
import cn105_adapter

class TestHttpServer(unittest.TestCase):
    def test_cn105_connect_response(self):
        req = cn105_adapter.CN105Response([0xfc, 0x7a, 0x01, 0x30, 0x01, 0x00, 0x54])
        self.assertTrue(str(req) == "CN105Response(type=0x7a, payload=[0x00])")
        self.assertTrue(req.packet_type == 0x7a)
        self.assertTrue(req.payload == [0x00])
        self.assertTrue(req.data == {})

    def test_cn105_getData_response(self):
        req = cn105_adapter.CN105Response([0xfc, 0x62, 0x01, 0x30, 0x10, 0x02, 0x00, 0x00, 0x00, 0x02, 0x0e, 0x00, 0x07, 0x00, 0x00, 0x03, 0xa2, 0x32, 0x00, 0x00, 0x00, 0x6d])
        self.assertTrue(str(req) == "CN105Response(type=0x62, payload=[0x02, 0x00, 0x00, 0x00, 0x02, 0x0e, 0x00, 0x07, 0x00, 0x00, 0x03, 0xa2, 0x32, 0x00, 0x00, 0x00])")
        self.assertTrue(req.packet_type == 0x62)
        self.assertTrue(req.payload == [0x02, 0x00, 0x00, 0x00, 0x02, 0x0e, 0x00, 0x07, 0x00, 0x00, 0x03, 0xa2, 0x32, 0x00, 0x00, 0x00])
        self.assertTrue(req.data == {'power': 0, 'mode': 2, 'tempSet': 14, 'fan': 0, 'vane': 7, 'dir': 3})
    
    def test_cn105_setData_response(self):
        req = cn105_adapter.CN105Response([0xfc, 0x61, 0x01, 0x30, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5e])
        self.assertTrue(str(req) == "CN105Response(type=0x61, payload=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])")
        self.assertTrue(req.packet_type == 0x61)
        self.assertTrue(req.payload == [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.assertTrue(req.data == {})