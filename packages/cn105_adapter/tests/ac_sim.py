
START_BYTE = 0xfc
PT_CONNECT_REQUEST = 0x5a
PT_CONNECT_RESPONSE = 0x7a
PT_GET_REQUEST = 0x42
PT_GET_RESPONSE = 0x62
PT_SET_REQUEST = 0x41
PT_SET_RESPONSE = 0x61

fields = {
    0x02:{
        "power": (3, 0x01),
        "mode": (4, 0x02),
        "tempSet": (5, 0x04),
        "fan": (6, 0x08),
        "vane": (7, 0x10),
        "dir": (10, 0x80),
    },
    0x03:{
        "tempRoom": (3, 0x00),
    }
}

class CN105SimResponse:
    def __init__(self, packet_type, payload):
        self.packet_type = packet_type
        self.payload = payload
        self.raw = [
            START_BYTE,
            packet_type,
            0x01, 0x30,
            len(payload)] + payload
        self.raw += self._crc()
    
    def _crc(self):
        return [0xfc - (sum(self.raw) & 0xff)]

    def __str__(self):
        return f"CN105SimResponse(type=0x{self.packet_type:02x}, payload=[{', '.join(f'0x{x:02x}' for x in self.payload)}])"


class CN105SimConnectResponse(CN105SimResponse):
    def __init__(self):
        super().__init__(packet_type=PT_CONNECT_RESPONSE, payload=[0x00])


class CN105SimGetDataResponse(CN105SimResponse):
    def __init__(self, rtype=0x02):
        super().__init__(packet_type=PT_GET_RESPONSE, payload=[rtype] + [0x00]*15)

class CN105SimRequest:
    def __init__(self, raw):
        self.raw = raw
        self.data = {}

        if len(raw) < 7:
            raise ValueError("Packet incomplete (shorter than 7 bytes)")

        if raw[0] != START_BYTE:
            raise ValueError("Packet doesn't start with expected start byte")

        if raw[1] not in [PT_CONNECT_REQUEST, PT_GET_REQUEST, PT_SET_REQUEST]:
            raise ValueError("Unknown packet type")

        self.packet_type = raw[1]

        if raw[2:4] != [0x01, 0x30]:
            raise ValueError("Wrong Header")
        
        payload_length = raw[4]
        
        if len(raw) < payload_length + 6:
            raise ValueError("Packet so short")
        
        if len(raw) > payload_length + 6:
            raise ValueError("Packet so long")
        
        self.payload = raw[5:5+payload_length]

        if not(self._check_crc()):
            raise ValueError("Wrong CRC")

        self._parse_payload()

    def _parse_payload(self):
        if self.packet_type == PT_GET_RESPONSE:
            rtype = self.payload[0]
            if self.payload[0] in [0x02, 0x03]:
                for key in fields[rtype]:
                    pos = fields[rtype][key][0]
                    self.data[key] = self.payload[pos]
        elif self.packet_type == PT_SET_RESPONSE:
            pass
        
    def __str__(self):
        return f"CN105SimRequest(type=0x{self.packet_type:02x}, payload=[{', '.join(f'0x{x:02x}' for x in self.payload)}])"

    def _check_crc(self):
        return 0xfc - (sum(self.raw[:-1]) & 0xff) == self.raw[-1]