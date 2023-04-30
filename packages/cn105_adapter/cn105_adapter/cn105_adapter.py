"""CN105_adapter

An adapter to control a Mitsubishi heat pump using the CN105 protocol.
"""

import sys

if sys.implementation.name == "cpython":
    import asyncio
    import platform
    if platform.node() == "Tobias-DellXPS":
        from serial_asyncio import open_serial_connection

if sys.implementation.name == "micropython":
    import uasyncio as asyncio
    from umachine import UART

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

powerMapping = [
    (0x00, "OFF"),
    (0x01, "ON")
]

modeMapping = [
    (0x01, "HEAT"),
    (0x02, "DRY"),
    (0x03, "COOL"),
    (0x07, "FAN"),
    (0x08, "AUTO")
]

tempSetMapping = [
    (31-i, i) for i in range(16, 32)
]

tempRoomMapping = [
    (i, 10+i) for i in range(0, 31)
]

fanMapping = [
    (0x00, "AUTO"),
    (0x01, "QUIET"),
    (0x02, "1"),
    (0x03, "2"),
    (0x05, "3"),
    (0x06, "4")
]

vaneMapping = [
    (0x00, "AUTO"),
    (0x01, "1"),
    (0x02, "2"),
    (0x03, "3"),
    (0x04, "4"),
    (0x05, "5"),
    (0x07, "SWING")
]

dirMapping = [
    (0x00, "NA"),
    (0x01, "<<"),
    (0x02, "<"),
    (0x03, "|"),
    (0x04, ">"),
    (0x05, ">>"),
    (0x08, "<>"),
    (0x0C, "SWING")
]

def rawToPhys(mapping: list[tuple], raw:int) -> str or int:
    """Converts the raw value to a physical value.

    Args:
        mapping (list[tuple]): The mapping. Could be `cn105_adapter.powerMapping`, `cn105_adapter.modeMapping`, 
            `cn105_adapter.tempSetMapping`, `cn105_adapter.tempRoomMapping`, `cn105_adapter.fanMapping`, 
            `cn105_adapter.vaneMapping` or `cn105_adapter.dirMapping`.
        raw (int): The raw value.

    Returns:
        str or int: The physical value.

    Example:
        >>> cn105_adapter.rawToPhys(cn105_adapter.powerMapping, 0)
        "OFF"
        
    """
    for t in mapping:
        if t[0] == raw:
            return t[1]

def physToRaw(mapping, phys:str or int):
    """Converts the physical value to a raw value.

    Args:
        mapping (list[tuple]): The mapping. Could be `cn105_adapter.powerMapping`, `cn105_adapter.modeMapping`, 
            `cn105_adapter.tempSetMapping`, `cn105_adapter.tempRoomMapping`, `cn105_adapter.fanMapping`, 
            `cn105_adapter.vaneMapping` or `cn105_adapter.dirMapping`.
        phys (str or int): The physical value.

    Returns:
        int: The raw value.

    Example:
        >>> cn105_adapter.physToRaw(cn105_adapter.powerMapping, "on")
        1
    """
    for t in mapping:
        if type(phys) is str:
            if t[1] == phys.upper():
                return t[0]
        else:    
            if t[1] == phys:
                return t[0]
        

class CN105Request:
    """A Basic Request for the Mitsubishi CN105-Protocol. You shouldn't have to create one by yourself.

        Args:
            packet_type (int): Type of the packet (CONNECT/GET/SET).
            payload (list[int]): The payload.
    """
    def __init__(self, packet_type:int, payload:list[int]):
        """Initializes the Request.

        Args:
            packet_type (int): Type of the packet (CONNECT/GET/SET).
            payload (list[int]): The payload.
        """
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
        return f"CN105Request(type=0x{self.packet_type:02x}, payload=[{', '.join(f'0x{x:02x}' for x in self.payload)}])"


class CN105ConnectRequest(CN105Request):
    """A Connect Request for the Mitsubishi CN105-Protocol. You shouldn't have to create one by yourself.
    """
    def __init__(self):
        super().__init__(packet_type=PT_CONNECT_REQUEST, payload=[0xCA, 0x01])


class CN105GetDataRequest(CN105Request):
    """A Get Data Request for the Mitsubishi CN105-Protocol. You shouldn't have to create one by yourself.

        Args:
            rtype (int, optional): Type of the Get Date request, 0x02 or 0x03. Defaults to 0x02.
    """
    def __init__(self, rtype:int=0x02):
        """Initializes the Get Data Request.

        Args:
            rtype (int, optional): Type of the Get Date request, 0x02 or 0x03. Defaults to 0x02.
        """
        super().__init__(packet_type=PT_GET_REQUEST, payload=[rtype] + [0x00]*15)


class CN105SetDataRequest(CN105Request):
    """A Set Data Request for the Mitsubishi CN105-Protocol. You shouldn't have to create one by yourself.

        Args:
            rtype (int, optional): Type of the Get Date request. Currently, only 0x02 is allowed. Defaults to 0x02.
            data (dict, optional): Data, that is set on the in this packet. Defaults to None.

        Raises:
            ValueError: If the dict is empty.
            ValueError: If the dict contains a key, that is not allowed in this packet.
    """
    def __init__(self, rtype:int=0x02, data:dict=None):
        """Initializes the Set Data Request.

        Args:
            rtype (int, optional): Type of the Get Date request. Currently, only 0x02 is allowed. Defaults to 0x02.
            data (dict, optional): Data, that is set on the in this packet. Defaults to None.

        Raises:
            ValueError: If the dict is empty.
            ValueError: If the dict contains a key, that is not allowed in this packet.
        """
        if (data is None) or (data == {}):
            raise ValueError("Empty data dict is not allowed")
        
        payload = [rtype] + [0x00]*15
        for key in data:
            if key not in fields[rtype]:
                raise ValueError(f"Key {key} is not allowed in this request")
            
            payload[1] |= fields[rtype][key][1]

            pos = fields[rtype][key][0]
            payload[pos] = data[key]

        super().__init__(packet_type=PT_SET_REQUEST, payload=payload)

class CN105Response:
    """A Response from the Mitsubishi CN105-Protocol. You shouldn't have to create one by yourself.

        Args:
            raw (bytes or list[int]): The data, that was received from the device.

        Raises:
            ValueError: If the raw content couldn't be parsed.
    """
    def __init__(self, raw:bytes or list[int]):
        """Initializes the Response and parses the payload.

        Args:
            raw (bytes or list[int]): The data, that was received from the device.

        Raises:
            ValueError: If the raw content couldn't be parsed.
        """
        if type(raw) is bytes:
            raw = [int(x) for x in raw]
        self.raw = raw
        self.data = {}

        if len(raw) < 7:
            raise ValueError("Packet incomplete (shorter than 7 bytes)")

        if raw[0] != START_BYTE:
            raise ValueError("Packet doesn't start with expected start byte")

        if raw[1] not in [PT_CONNECT_RESPONSE, PT_GET_RESPONSE, PT_SET_RESPONSE]:
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
        return f"CN105Response(type=0x{self.packet_type:02x}, payload=[{', '.join(f'0x{x:02x}' for x in self.payload)}])"

    def _check_crc(self):
        return 0xfc - (sum(self.raw[:-1]) & 0xff) == self.raw[-1]


class CN105Server:
    """A Server, that sends and receives packets to and from a CN105 Client.

        Args:
            tx (int, optional): The tx pin. Defaults to 17.
            rx (int, optional): The rx pin. Defaults to 16.
    """
    def __init__(self, tx:int=17, rx:int=16):
        """Initializes the Server

        Args:
            tx (int, optional): The tx pin. Defaults to 17.
            rx (int, optional): The rx pin. Defaults to 16.
        """
        if tx != 0:
            self.uart = UART(2, baudrate=2400, tx=tx, rx=rx, parity=0)
            self.uart.init(timeout=50)
            self.swriter = asyncio.StreamWriter(self.uart, {})
            self.sreader = asyncio.StreamReader(self.uart)
        self.connected = False
        self.waiting_for_response = False

    async def _start_sim(self):
        self.sreader, self.swriter = await open_serial_connection(url='COM50', baudrate=2400)

    def _stop_sim(self):
        self.swriter.close()
    
    async def _send_packet_and_wait_for_response(self, request: CN105Request) -> CN105Response:    
        # Wait, if another request is being processed
        while self.waiting_for_response:
            await asyncio.sleep(1)
            print("waiting...")

        print("Sending:   " + str(request))
        self.waiting_for_response = True
        self.swriter.write(bytearray(request.raw))
        await self.swriter.drain()
        raw = await self.sreader.read(30)
        self.waiting_for_response = False
        if raw is not None:
            response = CN105Response(raw)
            print("Receiving: " + str(response))
            return response
        
        raise ValueError("AC didn't responde")
        

    async def connect(self) -> bool:
        """Send a connect request to the CN105 device.

        Returns:
            bool: If the device returned a connect response.
        """
        print("Connecting to AC... ")
        request = CN105ConnectRequest()
        response = await self._send_packet_and_wait_for_response(request)
        self.connected = response.packet_type == PT_CONNECT_RESPONSE
        if self.connected:
            print("done")
        else:
            print("failed")
        return self.connected
    
    async def get_data(self, rtype: int) -> CN105Response:
        """Send a Get Data Request to the CN105 device.

        Args:
            rtype (int): The type of the Get Data Request (0x02 or 0x03).

        Returns:
            CN105Response: The Response, that was returned from the device.
        """
        print("Getting state of AC... ")
        request = CN105GetDataRequest(rtype=rtype)
        response = await self._send_packet_and_wait_for_response(request)
        if response.packet_type == PT_GET_RESPONSE:
            print("done")
            return response
        else:
            print("failed")
            return None

    async def set_data(self, data: dict) -> CN105Response:
        """Send a Set Data Request to the CN105 device.

        Args:
            data (dict): The data, that should be set on the device.

        Returns:
            CN105Response: The Response, that was returned from the device.
        """
        print("Setting state of AC... ")
        request = CN105SetDataRequest(data=data)
        response = await self._send_packet_and_wait_for_response(request)
        if response.packet_type == PT_SET_RESPONSE:
            print("done")
            return response
        else:
            print("failed")
            return None
        
    