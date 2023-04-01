"""
modbusBatch - batch modbus requests.

 Public Functions:
 build_batches - Bulk up to 120 registers into batches
 process_batches - Retrieves all registers from modbus server in one single composed request

 Internal Functions:
 _reg_CSV - Import csv-file with modbus-register declarations
 _CSV_to_MbReg -  Verify and complete an imported csv array (one line) and convert to MbReg
 _reg_YML - Import yml-File with modbus-register declarations - to be done
 _reg_JSON - Import json-File with modbus-register declarations - to be done

"""
import csv
import time
import dataclasses

import mbInverter
from modbusBatch.mbUtils import int_with_default, float_with_default, u16, u32be, u32le, s16, s32be, s32le, regs_to_str
from modbusBatch.modbusTcpRaw import ModbusTcpRaw
import logging
log = logging.getLogger(__name__)


class MbBatch(object):
    """ Batch Modbus Requests """

    @dataclasses.dataclass( frozen=False, eq=False, order=False )
    class MbReg:
        """ Modbus register information
            One instance represents one line in csv-definition.
            Public field-names must match column-names of csv-file
        """
        # public
        reg_type: str
        reg_number: int
        reg_name: str
        reg_desc: str
        measurement_unit: str
        data_type: str
        data_length: int
        unit_id: int
        scaling_factor: int | float
        reserved: str = None
        round: int = 1
        # private
        _field_decoder: object = None  # points to conversion function (binary to int etc.)

        @property
        def field_decoder(self):
            return self._field_decoder

        def shortinfo(self) -> str:
            return f'{self.reg_name}: {self.reg_type} {self.reg_number} {self.data_type}  {self.data_length} ' + \
                   f'{self.scaling_factor} '

    @dataclasses.dataclass( frozen=False, eq=False, order=False )
    class MbRequest:
        unit_id: int  # modbus unit
        address: int  # modbus register address
        quantity: int  # quantity of registers to read
        from_x: int  # first corresponding register in list of MbRegs
        to_x: int  # last corresponding register in list of MbRegs
        reg_type: str  # h = holding, i = input

    MbRequests = [MbRequest]
    MbRegs = [MbReg]

    def __init__(self, host="localhost", port=502, retry=3, reg_offset=0, reg_wordswap=True,
                 file_type="csv", file_path="registers.csv", inv_model=".foo.bar", inv_options=None):
        # private
        self._host = host
        self._port = port
        self._retry = retry
        self._reg_offset = reg_offset
        self._reg_wordswap = reg_wordswap
        self._file_type = file_type
        self._file_path = file_path
        self._inv_model = inv_model
        self._inv_options = inv_options
        self._callInverter = None
        self._csv_header = None
        # public
        self.mbregs: [MbBatch.MbReg] = list()
        self.mbrequests: [MbBatch.MbRequest] = list()
        self.results: dict = {}
        self.client = None

        """
        Is there a special function named <inv_model>?
        """
        if callable(getattr(mbInverter, self._inv_model)):
            mbInverter.afterModbusComplete = getattr(mbInverter, self._inv_model)
        else:
            mbInverter.afterModbusComplete = mbInverter.doNothing

        """ define ModbusTCP connection (raw version) """
        try:
            self.client = ModbusTcpRaw( host=self._host,
                                        port=self._port,
                                        unit_id=0,
                                        auto_open=False,
                                        auto_close=False )
        except Exception as e:
            log.error( "Error with host or port params", e )
            exit( 13 )

        if self._file_type.lower() == "csv":
            self._reg_CSV()
            self.build_batches()

        # to be done: json, yaml

    def _reg_CSV(self):
        """
        Import csv-file with modbus-register declarations
        and sort by unit_id, reg_type, reg_number
        """
        def _CSV_to_MbReg(_csv_record: list) -> MbBatch.MbReg:
            """ Verify and complete an imported csv array (one line) and convert to MbReg """
            MbBatch._helper = f">{_csv_record}<"
            d = dict( zip( self._csv_header, _csv_record ) )
            d['reg_number'] = int( d['reg_number'] )
            d['unit_id'] = int_with_default( d['unit_id'], 1 )
            if '.' in d['scaling_factor']:
                d['scaling_factor'] = float_with_default( d['scaling_factor'], 1. )
                if d['scaling_factor'] < 0.001:
                    d['round'] = 4
                elif d['scaling_factor'] < 0.01:
                    d['round'] = 3
                elif d['scaling_factor'] < 0.1:
                    d['round'] = 2
                else:
                    d['round'] = 1
            else:
                d['scaling_factor'] = int_with_default( d['scaling_factor'], 1 )
                d['round'] = 0

            if d['reg_desc'] == '':
                d['reg_desc'] = d['reg_name'].replace( '_', ' ' )

            d['reg_name'] = d["reg_name"].lower()
            d['measurement_unit'] = d['measurement_unit'].lower()
            d['data_type'] = d['data_type'].lower()
            d['data_length'] = int_with_default( d['data_length'], 1 )
            match d['data_type']:
                case 'chr':
                    d['data_length'] = max( 1, d["data_length"] )
                    d['_field_decoder'] = regs_to_str
                case 'str':
                    d['data_length'] = max( 1, d['data_length'] )
                    d['_field_decoder'] = regs_to_str
                case 'u32':
                    d['data_length'] = 2
                    d['_field_decoder'] = u32le if self._reg_wordswap else u32be
                case 's32':
                    d['data_length'] = 2
                    d['_field_decoder'] = s32le if self._reg_wordswap else s32be
                case 's16':
                    d['data_length'] = 1
                    d['_field_decoder'] = s16
                case _:
                    d['data_type'] = 'u16'
                    d['data_length'] = 1
                    d['_field_decoder'] = u16
            # make MbReg from dict:
            r = MbBatch.MbReg( **d )
            return r

        def _filter(_csv_record) -> bool:
            """
             Lines starting with "#" will be treated as comments and ignored
             First non-comment-line will is csv-header which should contain following fields:
             reg_type, reg_number, reg_name, reg_desc, measurement_unit, data_type, data_length, unit_id,
                                                                                                scaling_factor
            """
            if _csv_record[0][0] == '#' or len(_csv_record) < 3:
                return False
            if self._csv_header is None:
                self._csv_header = list(map(lambda x: x.strip(), _csv_record))
                return False
            return True

        try:
            f = open(self._file_path)
            self.mbregs = sorted(list(map(_CSV_to_MbReg, filter( _filter, csv.reader( f ) ) )),
                                 key=lambda a: '%3.3i %s1.1 %5.5i' % (a.unit_id, a.reg_type, a.reg_number) )
        except BaseException as e:
            log.error(f"Murks in {__name__}, : {e}" )
            exit(12)

    def build_batches(self):
        """
        Make batches up to 120 registers for modbus access.
        Reading single registers via modbusTCP is possible but inefficient,
        therefore we define reasonable blocks of registers with a max size of 120,
        which is the limit for TCP connections.
        """
        mbrequest = None
        for i, reg in enumerate(self.mbregs):
            if i == 0:
                mbrequest = MbBatch.MbRequest( unit_id=reg.unit_id,
                                               address=reg.reg_number - self._reg_offset,
                                               quantity=reg.data_length,
                                               from_x=i,
                                               to_x=i,
                                               reg_type=reg.reg_type )
            elif reg.data_length + reg.reg_number - self._reg_offset - mbrequest.address > 120 or \
                    mbrequest.reg_type != reg.reg_type or \
                    mbrequest.unit_id != reg.unit_id:
                self.mbrequests.append(mbrequest)
                mbrequest = MbBatch.MbRequest( unit_id=reg.unit_id,
                                               address=reg.reg_number - self._reg_offset,
                                               quantity=reg.data_length,
                                               from_x=i,
                                               to_x=i,
                                               reg_type=reg.reg_type )
            else:
                mbrequest.quantity = reg.data_length + reg.reg_number - self._reg_offset - mbrequest.address
                mbrequest.to_x = i

        self.mbrequests.append(mbrequest)

    def process_batches(self) -> bool:
        """
        Retrieve all registers from modbus server in one single composed request and store results
        in dict results
        """
        _retry = self._retry
        while _retry and self.client:
            self.client.open()
            rc = True
            for b in self.mbrequests:
                rc = True
                self.client.unit_id = b.unit_id
                if b.reg_type == "h":
                    raw_values = self.client.read_holding_raw( reg_addr=b.address, reg_nb=b.quantity )
                else:
                    raw_values = self.client.read_input_raw( reg_addr=b.address, reg_nb=b.quantity )
                if raw_values is None:
                    log.error(f"invalid modbus result for batch ", b, f" retry {_retry} " )
                    rc = False
                    break
                for mbreg in self.mbregs[b.from_x:b.to_x + 1]:
                    x = (mbreg.reg_number - b.address - self._reg_offset) * 2
                    y = x + mbreg.data_length * 2
                    self.results[mbreg.reg_name] = mbreg.field_decoder( raw_values[x:y], mbreg.scaling_factor,
                                                                        mbreg.round)
            self.client.close()
            if rc:
                mbInverter.afterModbusComplete(self.results, self._inv_options)
                return rc
            else:
                time.sleep(0.3)

        return False
