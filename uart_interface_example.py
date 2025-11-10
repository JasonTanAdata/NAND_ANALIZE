#!/usr/bin/env python3
"""
Example usage of UART Interface for NAND Flash Analyzer
Demonstrates how to use the UART interface function with various commands.
"""

from nand_analyzer import NANDAnalyzer
import json


def print_result(result: dict):
    """Pretty print the result dictionary."""
    print(json.dumps(result, indent=2))
    print()


def example_1_readdata_command():
    """Example 1: Using the readdata command."""
    print("=" * 70)
    print("Example 1: UART Interface - readdata Command")
    print("=" * 70)
    print("Command: readdata EC D3 51 95")
    print("Purpose: Parse NAND flash ID bytes")
    print()
    
    analyzer = NANDAnalyzer()
    result = analyzer.uart_interface("readdata EC D3 51 95")
    print_result(result)


def example_2_parseid_command():
    """Example 2: Using the parseid command."""
    print("=" * 70)
    print("Example 2: UART Interface - parseid Command")
    print("=" * 70)
    print("Command: parseid 2C DC 90 A6")
    print("Purpose: Parse ID bytes and identify manufacturer")
    print()
    
    analyzer = NANDAnalyzer()
    result = analyzer.uart_interface("parseid 2C DC 90 A6")
    print_result(result)


def example_3_checkblock_command():
    """Example 3: Using the checkblock command."""
    print("=" * 70)
    print("Example 3: UART Interface - checkblock Command")
    print("=" * 70)
    print("Command: checkblock 128 0 10 0")
    print("Purpose: Check for bad blocks in range 0-10 with 128KB block size")
    print()
    
    # Create sample data with bad blocks
    block_size = 128 * 1024
    good_block = b'\xFF' * block_size
    bad_block = b'\x00' + b'\xFF' * (block_size - 1)
    data = good_block + bad_block + good_block + bad_block + good_block
    
    analyzer = NANDAnalyzer(data)
    result = analyzer.uart_interface("checkblock 128 0 10 0")
    print_result(result)


def example_4_calcwear_command():
    """Example 4: Using the calcwear command."""
    print("=" * 70)
    print("Example 4: UART Interface - calcwear Command")
    print("=" * 70)
    print("Command: calcwear 2 0 100 0")
    print("Purpose: Calculate wear leveling with 2KB page size")
    print()
    
    # Create sample data: 60% written, 40% erased
    page_size = 2048
    written_pages = b'\xAB' * (page_size * 6)
    erased_pages = b'\xFF' * (page_size * 4)
    data = written_pages + erased_pages
    
    analyzer = NANDAnalyzer(data)
    result = analyzer.uart_interface("calcwear 2 0 100 0")
    print_result(result)


def example_5_error_handling():
    """Example 5: Error handling examples."""
    print("=" * 70)
    print("Example 5: UART Interface - Error Handling")
    print("=" * 70)
    
    analyzer = NANDAnalyzer()
    
    # Invalid format - too few parameters
    print("Test 1: Too few parameters")
    print("Command: readdata EC D3")
    result = analyzer.uart_interface("readdata EC D3")
    print_result(result)
    
    # Unknown command
    print("Test 2: Unknown command")
    print("Command: invalidcmd 00 00 00 00")
    result = analyzer.uart_interface("invalidcmd 00 00 00 00")
    print_result(result)
    
    # Invalid hex parameter
    print("Test 3: Invalid hex parameter")
    print("Command: readdata ZZ D3 51 95")
    result = analyzer.uart_interface("readdata ZZ D3 51 95")
    print_result(result)


def example_6_case_insensitive():
    """Example 6: Case insensitive commands."""
    print("=" * 70)
    print("Example 6: UART Interface - Case Insensitive Commands")
    print("=" * 70)
    
    analyzer = NANDAnalyzer()
    
    commands = [
        "READDATA EC D3 51 95",
        "ReadData EC D3 51 95",
        "readdata EC D3 51 95"
    ]
    
    for cmd in commands:
        print(f"Command: {cmd}")
        result = analyzer.uart_interface(cmd)
        print(f"Status: {result['status']}")
        print()


def example_7_multiple_manufacturers():
    """Example 7: Testing different manufacturer IDs."""
    print("=" * 70)
    print("Example 7: UART Interface - Different Manufacturers")
    print("=" * 70)
    
    analyzer = NANDAnalyzer()
    
    manufacturers = [
        ("Samsung", "parseid EC D3 51 95"),
        ("Hynix", "parseid AD DC 10 95"),
        ("Micron", "parseid 2C DC 90 A6"),
        ("Toshiba", "parseid 98 D3 90 26"),
    ]
    
    for name, cmd in manufacturers:
        print(f"Testing {name}:")
        print(f"Command: {cmd}")
        result = analyzer.uart_interface(cmd)
        if result['status'] == 'success':
            print(f"Detected: {result['manufacturer']}")
        print()


def example_8_integrated_workflow():
    """Example 8: Integrated workflow using multiple commands."""
    print("=" * 70)
    print("Example 8: UART Interface - Integrated Workflow")
    print("=" * 70)
    print("Simulating a complete NAND flash analysis workflow")
    print()
    
    # Step 1: Parse ID
    print("Step 1: Parse NAND Flash ID")
    analyzer = NANDAnalyzer()
    result = analyzer.uart_interface("parseid EC D3 51 95")
    print(f"Manufacturer: {result.get('manufacturer', 'Unknown')}")
    print()
    
    # Step 2: Read data with full info
    print("Step 2: Read data and get full flash info")
    result = analyzer.uart_interface("readdata EC D3 51 95")
    if result['status'] == 'success':
        flash_info = result['flash_info']
        print(f"Page Size: {flash_info['page_size']} bytes")
        print(f"Block Size: {flash_info['block_size']} bytes")
        print(f"Total Size: {flash_info['total_size'] / (1024**2):.2f} MB")
    print()
    
    # Step 3: Create sample data for analysis
    print("Step 3: Analyze sample data")
    block_size = 128 * 1024
    page_size = 2048
    
    # Create 10 blocks with some bad blocks
    blocks = []
    for i in range(10):
        if i in [2, 5]:  # Mark blocks 2 and 5 as bad
            blocks.append(b'\x00' + b'\xFF' * (block_size - 1))
        else:
            blocks.append(b'\xFF' * block_size)
    
    data = b''.join(blocks)
    analyzer.data = data
    
    # Step 4: Check for bad blocks
    print("Step 4: Check for bad blocks")
    result = analyzer.uart_interface("checkblock 128 0 9 0")
    if result['status'] == 'success':
        print(f"Total bad blocks: {result['total_bad_blocks']}")
        print(f"Bad blocks in range: {result['bad_blocks_in_range']}")
    print()
    
    # Step 5: Calculate wear leveling
    print("Step 5: Calculate wear leveling statistics")
    result = analyzer.uart_interface("calcwear 2 0 1000 0")
    if result['status'] == 'success':
        print(f"Total pages: {result['total_pages']}")
        print(f"Erased pages: {result['erased_pages']}")
        print(f"Written pages: {result['written_pages']}")
        print(f"Utilization: {result['utilization_percent']}%")
    print()


def main():
    """Run all UART interface examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "UART Interface Examples" + " " * 30 + "║")
    print("║" + " " * 20 + "NAND Flash Analyzer" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    example_1_readdata_command()
    example_2_parseid_command()
    example_3_checkblock_command()
    example_4_calcwear_command()
    example_5_error_handling()
    example_6_case_insensitive()
    example_7_multiple_manufacturers()
    example_8_integrated_workflow()
    
    print("=" * 70)
    print("All UART interface examples completed successfully!")
    print("=" * 70)
    print("\nSupported Commands:")
    print("  - readdata <id1> <id2> <id3> <id4>  : Parse ID bytes and get flash info")
    print("  - parseid <id1> <id2> <id3> <id4>   : Parse ID bytes only")
    print("  - checkblock <size_kb> <start> <end> <reserved> : Check bad blocks")
    print("  - calcwear <size_kb> <start> <end> <reserved>   : Calculate wear leveling")
    print()


if __name__ == "__main__":
    main()
