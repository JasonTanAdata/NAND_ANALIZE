# NAND_ANALIZE

A Python-based NAND flash memory analysis tool for parsing and analyzing NAND flash data.

## Features

- Parse NAND flash ID bytes to extract device information
- Identify NAND flash manufacturers
- Analyze bad blocks in NAND flash data
- Calculate and verify ECC (Error Correction Code)
- Analyze wear leveling statistics
- Generate comprehensive analysis reports

## Installation

```bash
git clone https://github.com/JasonTanAdata/NAND_ANALIZE.git
cd NAND_ANALIZE
pip install -r requirements.txt
```

## Usage

### Basic Usage - Parse ID Bytes

```bash
python nand_analyzer.py EC D3 51 95
```

This will parse the NAND flash ID bytes and display device information.

### Analyze NAND Flash Data File

```bash
python nand_analyzer.py EC D3 51 95 flash_data.bin
```

This will parse the ID bytes and analyze the data from the binary file.

### Programmatic Usage

```python
from nand_analyzer import NANDAnalyzer

# Create analyzer instance
analyzer = NANDAnalyzer()

# Parse ID bytes
id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
flash_info = analyzer.parse_id_bytes(id_bytes)

print(flash_info)
print(f"Manufacturer: {analyzer.get_manufacturer_name(flash_info.manufacturer_id)}")

# Analyze data if available
with open('flash_data.bin', 'rb') as f:
    data = f.read()
    
analyzer.data = data
bad_blocks = analyzer.analyze_bad_blocks(data, flash_info.block_size)
print(f"Bad blocks found: {len(bad_blocks)}")

# Generate full report
print(analyzer.generate_report())
```

## NAND Flash ID Bytes

NAND flash ID bytes typically contain:
- Byte 0: Manufacturer ID
- Byte 1: Device ID
- Byte 2: Cell information
- Byte 3: Page size and block size information
- Bytes 4+: Additional device-specific information

## Supported Manufacturers

- Samsung (0xEC)
- Toshiba (0x98)
- Hynix (0xAD)
- Micron (0x2C)
- And more...

## Testing

Run tests with pytest:

```bash
pytest test_nand_analyzer.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License
