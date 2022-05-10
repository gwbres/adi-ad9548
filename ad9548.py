#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# Class and macros to interact with AD9548 chipsets
#################################################################
from smbus import SMBus
class AD9548 :
    """ Class to interact with AD9548 chipset,
    only I2C bus supported @ the moment """
    def __init__ (self, bus, address):
        """ Creates an AD9546 device, 
        bus: [int] I2C bus number, X in /dev/i2c-X filesystem entry point   
        address: [int] i2c slave address
        """
        self.slv_addr = address
        self.handle = SMBus()
        self.handle.open(bus)
    
    def write_data (self, addr, data):
        """ Writes given data (uint8_t) to given address (uint16_t) """
        msb = (addr & 0xFF00)>>8
        lsb = addr & 0xFF
        self.handle.write_i2c_block_data(self.slv_addr, msb, [lsb, data & 0xFF])

    def read_data (self, addr):
        """ Reads data at given address (uint16_t) returns uint8_t """
        msb = (addr & 0xFF00)>>8
        lsb = addr & 0xFF
        self.handle.write_i2c_block_data(self.slv_addr, msb, [lsb])
        data = self.handle.read_byte(self.slv_addr)
        return data

    def io_update (self):
        """ Performs `I/O update` operation. 
        Refer to device datasheet """
        self.write_data(0x0005, 0x01)
