import unittest
import cn105_adapter
import asyncio
import sys
import platform
import ac_sim

if sys.implementation.name == "cpython":
    from serial_asyncio import open_serial_connection

class TestAscyncHttpServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if platform.node() != "Tobias-DellXPS":
            # Tests will fail, if there is no COM50 <--> COM51 connection.
            self.skipTest("specific setup required")
        self.sim_running = True

        async def run_sim():
            self.reader, self.writer = await open_serial_connection(url='COM51', baudrate=2400)
            while self.sim_running:
                raw = await self.reader.read(30)
                raw = [int(x) for x in raw]
                #print(" ".join([f"{x:02x}" for x in raw]))
                request = ac_sim.CN105SimRequest(raw)
                print(f"Server Receiving: {request}")
                if request.packet_type == ac_sim.PT_CONNECT_REQUEST:
                    response = ac_sim.CN105SimConnectResponse()
                if request.packet_type == ac_sim.PT_GET_REQUEST:
                    response = ac_sim.CN105SimGetDataResponse()
                print(f"Server Sending: {request}")
                self.writer.write(bytearray(response.raw))
                await self.writer.drain()

        self.task = asyncio.create_task(run_sim())
        return await super().asyncSetUp()

    async def asyncTearDown(self):
        self.sim_running = False
        self.writer.close()
        self.task.cancel()
        asyncio.ensure_future(self.task)
        return await super().asyncTearDown()
    
    async def test_connect(self):
        adp = cn105_adapter.CN105Server(tx=0)
        await adp._start_sim()
        await adp.connect()
        adp._stop_sim()
    
    async def test_getData(self):
        adp = cn105_adapter.CN105Server(tx=0)
        await adp._start_sim()
        await adp.connect()
        state = await adp.get_data(2)
        self.assertTrue(state.data == {'power': 0, 'mode': 0, 'tempSet': 0, 'fan': 0, 'vane': 0, 'dir': 0})
        adp._stop_sim()
        