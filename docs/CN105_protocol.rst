.. _CN105_protocol:

CN105 Protocol
**************

My Air Conditioning System uses the Mitsubishi CN105 protocol.
It is based on UART (2400 8E1).

There seem to be several different versions of this protocol. My AC (MSZ-HR25/35VF) works with this 
implementation.

Format
======

Each packet is constructed as follows: The initial byte, known as the synchronization byte, is set to 0xFC. 
This is followed by the packet type, which is represented by a single byte. Subsequently, two constant 
header bytes are included. After that, there is a single byte indicating the payload length, followed by a 
maximum of 16 bytes allocated for the payload itself. Finally, every packet concludes with a one-byte 
checksum to ensure data integrity.

+------------+-------------+------------+----------------+----------------+-----------------------------+
| Start Byte | Packet Type | Header     | Payload Length | Payload        | Checksum                    |
+============+=============+============+================+================+=============================+
| 0xFC       | 1 Byte      | 0x01, 0x30 | 1 Byte         | up to 16 Bytes | 0xFC - (Sum(Packet) & 0xFF) |
+------------+-------------+------------+----------------+----------------+-----------------------------+

Packet Types
============

There are six different packet types that work with my AC:

+------------------+-------+-------------------------------------+
| Type             | Value | Description                         |
+==================+=======+=====================================+
| Connect Request  | 0x5A  | Initiate Communication with AC      |
+------------------+-------+-------------------------------------+
| Connect Response | 0x7A  | Response from AC on Connect Request |
+------------------+-------+-------------------------------------+
| Get Request      | 0x42  | Request Readings from AC            |
+------------------+-------+-------------------------------------+
| Get Responses    | 0x62  | Response from AC on Get Request     |
+------------------+-------+-------------------------------------+
| Set Request      | 0x41  | Set State to AC                     |
+------------------+-------+-------------------------------------+
| Set Response     | 0x61  | Response from AC on Set Request     |
+------------------+-------+-------------------------------------+

Connect
-------

To initiate the communication with the AC, you have to send a connect request (packet type 0x5A) with the 
two byte payload 0xCA, 0x01. If everything goes well, the AC answers with a connect response (packet type 
0x7A) with a one byte payload 0x00:

+-----------+------------+-------------+------------+----------------+------------+----------+
| Direction | Start Byte | Packet Type | Header     | Payload Length | Payload    | Checksum |
+===========+============+=============+============+================+============+==========+
| to AC     | 0xFC       | 0x5A        | 0x01, 0x30 | 0x02           | 0xCA, 0x01 | 0xA8     |
+-----------+------------+-------------+------------+----------------+------------+----------+
| from AC   | 0xFC       | 0x7A        | 0x01, 0x30 | 0x01           | 0x00       | 0x54     |
+-----------+------------+-------------+------------+----------------+------------+----------+

The communication looks as followes::

    Sending:    fc 5a 01 30 02 ca 01 a8
    Receiving:  fc 7a 01 30 01 00 54

Get Data
--------

If you want to receive data from the AC, you have to send a get request packet (packet type 0x42). If everything 
goes well, the AC answers with a get response packet (packet type 0x62):

+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+
| Direction | Start Byte | Packet Type | Header     | Payload Length | Payload   | Checksum                    |
+===========+============+=============+============+================+===========+=============================+
| to AC     | 0xFC       | 0x42        | 0x01, 0x30 | 0x10           | 16 * 0x00 | 0xFC - (Sum(Packet) & 0xFF) |
+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+
| from AC   | 0xFC       | 0x62        | 0x01, 0x30 | 0x10           | 16 Bytes  | 0xFC - (Sum(Packet) & 0xFF) |
+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+

The payload send to the AC is always 16 zeros. Depending on the get request type (0x02 or 0x03), you get different 
readings:

+-----------+-----------------------+--------+--------+-----------+--------+----------+--------+--------+--------+--------+-----------+---------+---------+---------+---------+---------+
| Direction | Byte 0 (Request Type) | Byte 1 | Byte 2 | Byte 3    | Byte 4 | Byte 5   | Byte 6 | Byte 7 | Byte 8 | Byte 9 | Byte 10   | Byte 11 | Byte 12 | Byte 13 | Byte 14 | Byte 15 |
+===========+=======================+========+========+===========+========+==========+========+========+========+========+===========+=========+=========+=========+=========+=========+
| from AC   | 0x02                  | 0x00   | 0x00   | power     | mode   | temp set | fan    | vane   | 0x00   | 0x00   | direction | ?       | ?       | 0x00    | 0x00    | 0x00    |
+-----------+-----------------------+--------+--------+-----------+--------+----------+--------+--------+--------+--------+-----------+---------+---------+---------+---------+---------+
| from AC   | 0x03                  | 0x00   | 0x00   | temp room | 0x00   | 0x00     | 0x00   | 0x00   | 0x00   | 0x00   | 0x00      | 0x00    | 0x00    | 0x00    | 0x00    | 0x00    |
+-----------+-----------------------+--------+--------+-----------+--------+----------+--------+--------+--------+--------+-----------+---------+---------+---------+---------+---------+

The Bytes maked with "?" are not always zero, but the meaning is unclear.

Example: 
Read the state of the AC

+-----------+------------+-------------+------------+----------------+------------------------------------------------------------------------------------------------+----------+
| Direction | Start Byte | Packet Type | Header     | Payload Length | Payload                                                                                        | Checksum |
+===========+============+=============+============+================+================================================================================================+==========+
| from AC   | 0xFC       | 0x61        | 0x01, 0x30 | 0x10           | 0x02, 0x00, 0x00, 0x01, 0x01, 0x0E, 0x00, 0x07, 0x00, 0x00, 0x03, 0xA2, 0x32, 0x00, 0x00, 0x00 | 0x6D     |
+-----------+------------+-------------+------------+----------------+------------------------------------------------------------------------------------------------+----------+

That means:

* Power: 0x01 (ON)
* Mode: 0x01 (HEAT)
* Temp: 0x0E (17°C)
* Fan: 0x00 (AUTO)
* Vane: 0x07 (SWING)
* Dir: 0x03 (\|)

Set Data
--------

If you want to set the state of the AC, you have to send a set request packet (packet type 0x41). If everything goes
well, you get a ser response packet (packet type 0x61).

+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+
| Direction | Start Byte | Packet Type | Header     | Payload Length | Payload   | Checksum                    |
+===========+============+=============+============+================+===========+=============================+
| to AC     | 0xFC       | 0x41        | 0x01, 0x30 | 0x10           | 16 Bytes  | 0xFC - (Sum(Packet) & 0xFF) |
+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+
| from AC   | 0xFC       | 0x61        | 0x01, 0x30 | 0x10           | 16 * 0x00 | 0xFC - (Sum(Packet) & 0xFF) |
+-----------+------------+-------------+------------+----------------+-----------+-----------------------------+

Payloads of set data packet:

+-----------+-----------------------+-------------+--------+--------+--------+----------+--------+--------+--------+--------+-----------+---------+---------+---------+---------+---------+
| Direction | Byte 0 (Request Type) | Byte 1      | Byte 2 | Byte 3 | Byte 4 | Byte 5   | Byte 6 | Byte 7 | Byte 8 | Byte 9 | Byte 10   | Byte 11 | Byte 12 | Byte 13 | Byte 14 | Byte 15 |
+===========+=======================+=============+========+========+========+==========+========+========+========+========+===========+=========+=========+=========+=========+=========+
| to AC     | 0x01                  | what is set | 0x00   | power  | mode   | temp set | fan    | vane   | 0x00   | 0x00   | direction | 0x00    | 0x00    | 0x00    | 0x00    | 0x00    |
+-----------+-----------------------+-------------+--------+--------+--------+----------+--------+--------+--------+--------+-----------+---------+---------+---------+---------+---------+

Byte 1 of the Set Data Packet is bitwise encoded. If you want to write the value, you have to have to set the
correspondig bit:

+-----+---------------------------------------+
| Bit | Meaning                               |
+=====+=======================================+
| 0   | Power state is written in this packet |
+-----+---------------------------------------+
| 1   | Mode is written in this packet        |
+-----+---------------------------------------+
| 2   | Temperature is written in this packet |
+-----+---------------------------------------+
| 3   | Fan is written in this packet         |
+-----+---------------------------------------+
| 4   | Vane is written in this packet        |
+-----+---------------------------------------+
| 7   | Direction is written in this packet   |
+-----+---------------------------------------+

Example: 

If you want to set the mode to heat and let the rest unchanged, the communication would look like this:

+-----------+------------+-------------+------------+----------------+------------------------------------------------------------------------------------------------+----------+
| Direction | Start Byte | Packet Type | Header     | Payload Length | Payload                                                                                        | Checksum |
+===========+============+=============+============+================+================================================================================================+==========+
| to AC     | 0xFC       | 0x41        | 0x01, 0x30 | 0x10           | 0x01, 0x02, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 | 0x7A     |
+-----------+------------+-------------+------------+----------------+------------------------------------------------------------------------------------------------+----------+
| from AC   | 0xFC       | 0x61        | 0x01, 0x30 | 0x10           | 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 | 0x5E     |
+-----------+------------+-------------+------------+----------------+------------------------------------------------------------------------------------------------+----------+

State/Readings encoding
=======================

The state or readings are encoded as follows:

Power
-----

+------+------+
| Raw  | Phys |
+======+======+
| 0x00 | OFF  |
+------+------+
| 0x01 | ON   |
+------+------+

Mode
----

+------+------+
| Raw  | Phys |
+======+======+
| 0x01 | HEAT |
+------+------+
| 0x02 | DRY  |
+------+------+
| 0x03 | COOL |
+------+------+
| 0x07 | FAN  |
+------+------+
| 0x08 | AUTO |
+------+------+

Set Temperature
---------------

For the set temperature you can use the following formula::

    phys = 31 - raw

So for example the raw value 0x08 means 23°C.

Room Temperature
----------------

The formula for the room temperature is different from the set temperature::

    phys = 10 + raw

So for example the raw value 0x08 means 18°C.

Fan
---

+------+-------+
| Raw  | Phys  |
+======+=======+
| 0x00 | AUTO  |
+------+-------+
| 0x01 | QUIET |
+------+-------+
| 0x02 | 1     |
+------+-------+
| 0x03 | 2     |
+------+-------+
| 0x05 | 3     |
+------+-------+
| 0x06 | 4     |
+------+-------+

Vane
----

+------+-------+
| Raw  | Phys  |
+======+=======+
| 0x00 | AUTO  |
+------+-------+
| 0x01 | 1     |
+------+-------+
| 0x02 | 2     |
+------+-------+
| 0x03 | 3     |
+------+-------+
| 0x04 | 4     |
+------+-------+
| 0x05 | 5     |
+------+-------+
| 0x07 | SWING |
+------+-------+

Direction
---------

The direction can't be set on my MSZ-HR25/35VF (because there is no wing for that), but maybe someone else
could use it:

+------+-------+
| Raw  | Phys  |
+======+=======+
| 0x00 | NA    |
+------+-------+
| 0x01 | <<    |
+------+-------+
| 0x02 | <     |
+------+-------+
| 0x03 |  \|   |
+------+-------+
| 0x04 | >     |
+------+-------+
| 0x05 | >>    |
+------+-------+
| 0x08 | <>    |
+------+-------+
| 0x0C | SWING |
+------+-------+

Example Communication
=====================

Here is an example communication, you can use for debugging or to build test cases::

    # Connecting
    Sending:    fc 5a 01 30 02 ca 01 a8
    Receiving:  fc 7a 01 30 01 00 54

    # Get Data
    Sending:    fc 42 01 30 10 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 7b
    Receiving:  fc 62 01 30 10 02 00 00 00 02 0e 00 07 00 00 03 a2 32 00 00 00 6d
    {'MODE': 2, 'TEMP': 14, 'DIR': 3, 'VANE': 7, 'FAN': 0, 'POWER': 0}
    {'MODE': 'DRY', 'TEMP': 17, 'DIR': '|', 'VANE': 'SWING', 'FAN': 'AUTO', 'POWER': 'OFF'}

    # Set Data (turn on AC)
    Sending:    fc 41 01 30 10 01 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 7b
    Receiving:  fc 61 01 30 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 5e
    # New State is
    Sending:    fc 42 01 30 10 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 7b
    Receiving:  fc 62 01 30 10 02 00 00 01 02 0e 00 07 00 00 03 a2 32 00 00 00 6c
    {'MODE': 2, 'TEMP': 14, 'DIR': 3, 'VANE': 7, 'FAN': 0, 'POWER': 1}
    {'MODE': 'DRY', 'TEMP': 17, 'DIR': '|', 'VANE': 'SWING', 'FAN': 'AUTO', 'POWER': 'ON'}

    # Set Data (set mode to HEAT)
    Sending:    fc 41 01 30 10 01 02 00 00 01 00 00 00 00 00 00 00 00 00 00 00 7a
    Receiving:  fc 61 01 30 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 5e
    # New State is
    Sending:    fc 42 01 30 10 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 7b
    Receiving:  fc 62 01 30 10 02 00 00 01 01 0e 00 07 00 00 03 a2 32 00 00 00 6d
    {'MODE': 1, 'TEMP': 14, 'DIR': 3, 'VANE': 7, 'FAN': 0, 'POWER': 1}
    {'MODE': 'HEAT', 'TEMP': 17, 'DIR': '|', 'VANE': 'SWING', 'FAN': 'AUTO', 'POWER': 'ON'}
