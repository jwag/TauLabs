MEMORY
{
    BL_FLASH (rx) : ORIGIN = 0x08000000,        LENGTH = 0x03000 - 0x00080
    BD_INFO (r)   : ORIGIN = 0x08003000 - 0x80, LENGTH =           0x00080
    FLASH (rx)    : ORIGIN = 0x08003000,        LENGTH = 0x20000 - 0x03000 - 0x00400
    EE_FLASH (rw) : ORIGIN = 0x0801FC00,        LENGTH = 0x00400
    SRAM (rwx)    : ORIGIN = 0x20000000,        LENGTH = 0x05000
}
