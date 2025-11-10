#!/usr/bin/env python3
"""
NAND Flash Analyzer
A tool for analyzing NAND flash memory data and properties.
"""

import struct
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NANDFlashInfo:
    """NAND Flash information structure."""
    manufacturer_id: int
    device_id: int
    page_size: int
    block_size: int
    total_size: int
    spare_size: int
    
    def __str__(self) -> str:
        return (
            f"NAND Flash Information:\n"
            f"  Manufacturer ID: 0x{self.manufacturer_id:02X}\n"
            f"  Device ID: 0x{self.device_id:02X}\n"
            f"  Page Size: {self.page_size} bytes\n"
            f"  Block Size: {self.block_size} bytes\n"
            f"  Total Size: {self.total_size / (1024**2):.2f} MB\n"
            f"  Spare Size: {self.spare_size} bytes"
        )


class NANDAnalyzer:
    """Main NAND Flash Analyzer class."""
    
    # Common NAND manufacturer IDs
    MANUFACTURERS = {
        0xEC: "Samsung",
        0x98: "Toshiba",
        0x04: "Fujitsu",
        0x8F: "National",
        0x07: "Renesas",
        0x20: "STMicro",
        0xAD: "Hynix",
        0x2C: "Micron",
        0x01: "AMD/Spansion",
        0xC2: "Macronix",
    }
    
    def __init__(self, data: Optional[bytes] = None):
        """Initialize NAND Analyzer with optional data."""
        self.data = data
        self.flash_info: Optional[NANDFlashInfo] = None
        
    def parse_id_bytes(self, id_bytes: bytes) -> NANDFlashInfo:
        """
        Parse NAND flash ID bytes to extract flash information.
        
        Args:
            id_bytes: ID bytes read from NAND flash (typically 5-8 bytes)
            
        Returns:
            NANDFlashInfo object with parsed information
        """
        if len(id_bytes) < 4:
            raise ValueError("ID bytes must be at least 4 bytes long")
        
        manufacturer_id = id_bytes[0]
        device_id = id_bytes[1]
        
        # Parse size information from byte 3 and 4
        # This is a simplified parser - actual NAND ID parsing is more complex
        cell_info = id_bytes[2] if len(id_bytes) > 2 else 0
        page_size_code = (id_bytes[3] & 0x03) if len(id_bytes) > 3 else 0
        block_size_code = ((id_bytes[3] >> 4) & 0x03) if len(id_bytes) > 3 else 0
        
        # Calculate page size (1KB, 2KB, 4KB, 8KB)
        page_size = 1024 * (2 ** page_size_code)
        
        # Calculate block size (64KB, 128KB, 256KB, 512KB)
        block_size = 64 * 1024 * (2 ** block_size_code)
        
        # Estimate spare size based on page size
        spare_size = page_size // 32  # Typical 1/32 ratio
        
        # Total size estimation (this would need more info in real scenario)
        total_size = block_size * 1024  # Assume 1024 blocks
        
        self.flash_info = NANDFlashInfo(
            manufacturer_id=manufacturer_id,
            device_id=device_id,
            page_size=page_size,
            block_size=block_size,
            total_size=total_size,
            spare_size=spare_size
        )
        
        return self.flash_info
    
    def get_manufacturer_name(self, manufacturer_id: int) -> str:
        """Get manufacturer name from ID."""
        return self.MANUFACTURERS.get(manufacturer_id, f"Unknown (0x{manufacturer_id:02X})")
    
    def analyze_bad_blocks(self, data: bytes, block_size: int) -> List[int]:
        """
        Analyze data for bad blocks.
        Bad blocks are typically marked with non-0xFF values in the spare area.
        
        Args:
            data: Raw NAND flash data
            block_size: Size of each block in bytes
            
        Returns:
            List of bad block numbers
        """
        bad_blocks = []
        num_blocks = len(data) // block_size
        
        for block_num in range(num_blocks):
            block_start = block_num * block_size
            block_data = data[block_start:block_start + block_size]
            
            # Check if block is marked as bad
            # Bad blocks are typically marked with first byte being non-0xFF
            if block_data and block_data[0] != 0xFF:
                bad_blocks.append(block_num)
        
        return bad_blocks
    
    def calculate_ecc(self, data: bytes) -> int:
        """
        Calculate simple ECC (Error Correction Code) for data.
        This is a simplified implementation for demonstration.
        
        Args:
            data: Data to calculate ECC for
            
        Returns:
            ECC value
        """
        ecc = 0
        for byte in data:
            ecc ^= byte
        return ecc
    
    def verify_ecc(self, data: bytes, expected_ecc: int) -> bool:
        """
        Verify ECC for given data.
        
        Args:
            data: Data to verify
            expected_ecc: Expected ECC value
            
        Returns:
            True if ECC matches, False otherwise
        """
        calculated_ecc = self.calculate_ecc(data)
        return calculated_ecc == expected_ecc
    
    def analyze_wear_leveling(self, data: bytes, page_size: int) -> Dict[str, int]:
        """
        Analyze wear leveling statistics.
        
        Args:
            data: Raw NAND flash data
            page_size: Size of each page in bytes
            
        Returns:
            Dictionary with wear leveling statistics
        """
        num_pages = len(data) // page_size
        erased_pages = 0
        written_pages = 0
        
        for page_num in range(num_pages):
            page_start = page_num * page_size
            page_data = data[page_start:page_start + page_size]
            
            # Check if page is erased (all 0xFF)
            if all(b == 0xFF for b in page_data[:min(64, len(page_data))]):
                erased_pages += 1
            else:
                written_pages += 1
        
        return {
            "total_pages": num_pages,
            "erased_pages": erased_pages,
            "written_pages": written_pages,
            "utilization_percent": (written_pages / num_pages * 100) if num_pages > 0 else 0
        }
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive analysis report.
        
        Returns:
            Formatted report string
        """
        if not self.flash_info:
            return "No flash information available. Please parse ID bytes first."
        
        report = ["=" * 50]
        report.append("NAND FLASH ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        report.append(str(self.flash_info))
        report.append("")
        report.append(f"Manufacturer: {self.get_manufacturer_name(self.flash_info.manufacturer_id)}")
        
        if self.data:
            report.append("")
            report.append("Data Analysis:")
            report.append(f"  Data Size: {len(self.data)} bytes")
            
            # Analyze bad blocks if we have enough data
            if len(self.data) >= self.flash_info.block_size:
                bad_blocks = self.analyze_bad_blocks(self.data, self.flash_info.block_size)
                report.append(f"  Bad Blocks: {len(bad_blocks)}")
                if bad_blocks:
                    report.append(f"  Bad Block Numbers: {bad_blocks[:10]}" + 
                                (" ..." if len(bad_blocks) > 10 else ""))
            
            # Analyze wear leveling
            wear_stats = self.analyze_wear_leveling(self.data, self.flash_info.page_size)
            report.append("")
            report.append("Wear Leveling Statistics:")
            report.append(f"  Total Pages: {wear_stats['total_pages']}")
            report.append(f"  Erased Pages: {wear_stats['erased_pages']}")
            report.append(f"  Written Pages: {wear_stats['written_pages']}")
            report.append(f"  Utilization: {wear_stats['utilization_percent']:.2f}%")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)


def main():
    """Main entry point for command-line usage."""
    print("NAND Flash Analyzer")
    print("-" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python nand_analyzer.py <id_bytes_hex>")
        print("Example: python nand_analyzer.py EC D3 51 95")
        print("\nOr with data file:")
        print("Usage: python nand_analyzer.py <id_bytes_hex> <data_file>")
        sys.exit(1)
    
    # Parse ID bytes from command line arguments
    id_bytes_hex = sys.argv[1:]
    
    # Check if last argument is a file
    data = None
    if len(id_bytes_hex) > 4:
        try:
            with open(id_bytes_hex[-1], 'rb') as f:
                data = f.read()
            id_bytes_hex = id_bytes_hex[:-1]
        except (FileNotFoundError, PermissionError):
            pass
    
    # Convert hex strings to bytes
    try:
        id_bytes = bytes([int(b, 16) for b in id_bytes_hex])
    except ValueError:
        print(f"Error: Invalid hex bytes. Please provide hex values like: EC D3 51 95")
        sys.exit(1)
    
    # Create analyzer and parse
    analyzer = NANDAnalyzer(data)
    
    try:
        flash_info = analyzer.parse_id_bytes(id_bytes)
        print(analyzer.generate_report())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
