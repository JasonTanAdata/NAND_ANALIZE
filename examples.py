#!/usr/bin/env python3
"""
Example usage of NAND Flash Analyzer
"""

from nand_analyzer import NANDAnalyzer
import os


def example_1_parse_id_bytes():
    """Example 1: Parse NAND flash ID bytes."""
    print("=" * 60)
    print("Example 1: Parse NAND Flash ID Bytes")
    print("=" * 60)
    
    # Samsung K9F2G08U0M ID bytes
    analyzer = NANDAnalyzer()
    id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
    
    flash_info = analyzer.parse_id_bytes(id_bytes)
    print(flash_info)
    print(f"\nManufacturer: {analyzer.get_manufacturer_name(flash_info.manufacturer_id)}")
    print()


def example_2_analyze_sample_data():
    """Example 2: Analyze sample NAND flash data."""
    print("=" * 60)
    print("Example 2: Analyze Sample NAND Flash Data")
    print("=" * 60)
    
    # Create sample data
    page_size = 2048
    block_size = 128 * 1024
    
    # Create 4 blocks of data
    # Block 0: Erased (all 0xFF)
    # Block 1: Written with some data
    # Block 2: Bad block (starts with 0x00)
    # Block 3: Partially written
    
    block_0 = b'\xFF' * block_size  # Erased
    block_1 = b'\xAB' * block_size  # Written
    block_2 = b'\x00' + b'\xFF' * (block_size - 1)  # Bad block marker
    block_3 = (b'\x12\x34\x56\x78' * (block_size // 4))[:block_size]  # Partially written
    
    sample_data = block_0 + block_1 + block_2 + block_3
    
    # Analyze the data
    analyzer = NANDAnalyzer(sample_data)
    id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
    analyzer.parse_id_bytes(id_bytes)
    
    # Check for bad blocks
    bad_blocks = analyzer.analyze_bad_blocks(sample_data, block_size)
    print(f"Bad blocks found: {bad_blocks}")
    
    # Analyze wear leveling
    wear_stats = analyzer.analyze_wear_leveling(sample_data, page_size)
    print(f"\nWear Leveling Statistics:")
    print(f"  Total pages: {wear_stats['total_pages']}")
    print(f"  Erased pages: {wear_stats['erased_pages']}")
    print(f"  Written pages: {wear_stats['written_pages']}")
    print(f"  Utilization: {wear_stats['utilization_percent']:.2f}%")
    print()


def example_3_ecc_calculation():
    """Example 3: Calculate and verify ECC."""
    print("=" * 60)
    print("Example 3: Calculate and Verify ECC")
    print("=" * 60)
    
    analyzer = NANDAnalyzer()
    
    # Sample data
    data = b"Hello, NAND Flash!"
    
    # Calculate ECC
    ecc = analyzer.calculate_ecc(data)
    print(f"Data: {data}")
    print(f"Calculated ECC: 0x{ecc:02X}")
    
    # Verify ECC
    is_valid = analyzer.verify_ecc(data, ecc)
    print(f"ECC verification: {'PASS' if is_valid else 'FAIL'}")
    
    # Test with corrupted data
    corrupted_data = b"Hello, NAND Flash?"  # Changed last character
    is_valid_corrupted = analyzer.verify_ecc(corrupted_data, ecc)
    print(f"Corrupted data verification: {'PASS' if is_valid_corrupted else 'FAIL'}")
    print()


def example_4_full_report():
    """Example 4: Generate full analysis report."""
    print("=" * 60)
    print("Example 4: Generate Full Analysis Report")
    print("=" * 60)
    
    # Create sample data with various patterns
    page_size = 2048
    block_size = 128 * 1024
    
    sample_data = b'\xFF' * (block_size * 2) + b'\x5A' * (block_size * 2)
    
    analyzer = NANDAnalyzer(sample_data)
    id_bytes = bytes([0x2C, 0xDC, 0x90, 0xA6])  # Micron MT29F4G08
    analyzer.parse_id_bytes(id_bytes)
    
    # Generate and print report
    report = analyzer.generate_report()
    print(report)
    print()


def example_5_manufacturer_lookup():
    """Example 5: Look up different manufacturers."""
    print("=" * 60)
    print("Example 5: NAND Flash Manufacturer Lookup")
    print("=" * 60)
    
    analyzer = NANDAnalyzer()
    
    manufacturers = [
        (0xEC, "Samsung"),
        (0x98, "Toshiba"),
        (0xAD, "Hynix"),
        (0x2C, "Micron"),
        (0x01, "AMD/Spansion"),
        (0x20, "STMicro"),
    ]
    
    print("Known NAND Flash Manufacturers:")
    for mfg_id, expected_name in manufacturers:
        name = analyzer.get_manufacturer_name(mfg_id)
        print(f"  0x{mfg_id:02X}: {name}")
    
    # Unknown manufacturer
    unknown_name = analyzer.get_manufacturer_name(0xFF)
    print(f"  0xFF: {unknown_name}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "NAND Flash Analyzer Examples" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    example_1_parse_id_bytes()
    example_2_analyze_sample_data()
    example_3_ecc_calculation()
    example_4_full_report()
    example_5_manufacturer_lookup()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
