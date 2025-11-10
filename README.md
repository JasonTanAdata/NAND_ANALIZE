# NAND_ANALIZE

A Python-based NAND flash memory analysis tool for parsing and analyzing NAND flash data.

## Features

- Parse NAND flash ID bytes to extract device information
- Identify NAND flash manufacturers
- Analyze bad blocks in NAND flash data
- Calculate and verify ECC (Error Correction Code)
- Analyze wear leveling statistics
- Generate comprehensive analysis reports
- **NEW: UART Interface** - Command-line interface for NAND operations with structured command format

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

### UART Interface Usage

The UART interface provides a structured command format for NAND operations:

**Format:** `command parameter1 parameter2 parameter3 parameter4`

```python
from nand_analyzer import NANDAnalyzer

analyzer = NANDAnalyzer()

# Parse ID bytes and get flash information
result = analyzer.uart_interface("readdata EC D3 51 95")
print(result)

# Parse ID only
result = analyzer.uart_interface("parseid 2C DC 90 A6")
print(f"Manufacturer: {result['manufacturer']}")

# Check for bad blocks (requires data to be loaded)
analyzer.data = load_data()  # Load your data
result = analyzer.uart_interface("checkblock 128 0 10 0")
print(f"Bad blocks: {result['bad_blocks_in_range']}")

# Calculate wear leveling statistics
result = analyzer.uart_interface("calcwear 2 0 100 0")
print(f"Utilization: {result['utilization_percent']}%")
```

#### Supported UART Commands

1. **readdata** - Parse NAND flash ID bytes and get complete flash information
   - Format: `readdata <id_byte1> <id_byte2> <id_byte3> <id_byte4>`
   - Example: `readdata EC D3 51 95`
   - Returns: Complete flash info including manufacturer, page size, block size, etc.

2. **parseid** - Parse ID bytes and identify manufacturer only
   - Format: `parseid <id_byte1> <id_byte2> <id_byte3> <id_byte4>`
   - Example: `parseid AD DC 10 95`
   - Returns: Manufacturer name and ID information

3. **checkblock** - Check for bad blocks in a specified range
   - Format: `checkblock <block_size_kb> <start_block> <end_block> <reserved>`
   - Example: `checkblock 128 0 10 0`
   - Returns: List of bad blocks in the specified range
   - Note: Requires data to be loaded first

4. **calcwear** - Calculate wear leveling statistics
   - Format: `calcwear <page_size_kb> <start_page> <end_page> <reserved>`
   - Example: `calcwear 2 0 100 0`
   - Returns: Wear leveling statistics including utilization percentage
   - Note: Requires data to be loaded first

For detailed examples, see `uart_interface_example.py`.

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
