
""" pyModbusTCP Client with two additional methods "read_holding_raw" and "read_input_raw"
    based on https://github.com/sourceperl/pyModbusTCP from l.lefebvre
"""
import struct

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.constants import READ_INPUT_REGISTERS, READ_HOLDING_REGISTERS, MB_RECV_ERR



class ModbusTcpRaw( ModbusClient ):
    def read_holding_raw(self, reg_addr, reg_nb=1):
        """Modbus function READ_HOLDING_REGISTERS (0x03).

        :param reg_addr: register address (0 to 65535)
        :dev_type reg_addr: int
        :param reg_nb: number of registers to read (1 to 125)
        :dev_type reg_nb: int
        :returns: registers list or None if fail
        :rtype: list of register items (byte, network order = big endian)
        """
        # check params
        if not 0 <= int( reg_addr ) <= 0xffff:
            raise ValueError( 'reg_addr out of range (valid from 0 to 65535)' )
        if not 1 <= int( reg_nb ) <= 125:
            raise ValueError( 'reg_nb out of range (valid from 1 to 125)' )
        if int( reg_addr ) + int( reg_nb ) > 0x10000:
            raise ValueError( 'read after end of modbus address space' )
        # make request
        try:
            tx_pdu = struct.pack( '>BHH', READ_HOLDING_REGISTERS, reg_addr, reg_nb )
            rx_pdu = self._req_pdu( tx_pdu=tx_pdu, rx_min_len=3 )
            # extract field "byte count"
            byte_count = rx_pdu[1]
            # frame with regs value
            f_regs = rx_pdu[2:]
            # check rx_byte_count: buffer size must be consistent and have at least the requested number of registers
            if byte_count < 2 * reg_nb or byte_count != len( f_regs ):
                raise ModbusClient._NetworkError( MB_RECV_ERR, 'rx byte count mismatch' )
            # return raw registers
            return f_regs
        # handle error during request
        except ModbusClient._InternalError as e:
            self._req_except_handler( e )
            return None

    def read_input_raw(self, reg_addr, reg_nb=1):
        """Modbus function READ_INPUT_REGISTERS (0x04).

        :param reg_addr: register address (0 to 65535)
        :dev_type reg_addr: int
        :param reg_nb: number of registers to read (1 to 125)
        :dev_type reg_nb: int
        :returns: registers list or None if fail
        :rtype: list of register items (byte, network order = big endian)
        """
        # check params
        if not 0 <= int( reg_addr ) <= 0xffff:
            raise ValueError( 'reg_addr out of range (valid from 0 to 65535)' )
        if not 1 <= int( reg_nb ) <= 125:
            raise ValueError( 'reg_nb out of range (valid from 1 to 125)' )
        if int( reg_addr ) + int( reg_nb ) > 0x10000:
            raise ValueError( 'read after end of modbus address space' )
        # make request
        try:
            tx_pdu = struct.pack( '>BHH', READ_INPUT_REGISTERS, reg_addr, reg_nb )
            rx_pdu = self._req_pdu( tx_pdu=tx_pdu, rx_min_len=3 )
            # extract field "byte count"
            byte_count = rx_pdu[1]
            # frame with regs value
            f_regs = rx_pdu[2:]
            # check rx_byte_count: buffer size must be consistent and have at least the requested number of registers
            if byte_count < 2 * reg_nb or byte_count != len( f_regs ):
                raise ModbusClient._NetworkError( MB_RECV_ERR, 'rx byte count mismatch' )
            # return registers list
            return f_regs
        # handle error during request
        except ModbusClient._InternalError as e:
            self._req_except_handler( e )
            return None
