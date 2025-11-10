#!/usr/bin/env python3
"""
Unit tests for NAND Flash Analyzer
"""

import pytest
from nand_analyzer import NANDAnalyzer, NANDFlashInfo


class TestNANDAnalyzer:
    """Test cases for NANDAnalyzer class."""
    
    # Test constants
    TEST_BLOCK_SIZE = 128 * 1024  # 128KB block size for tests
    TEST_PAGE_SIZE = 2048  # 2KB page size for tests
    
    def test_initialization(self):
        """Test NANDAnalyzer initialization."""
        analyzer = NANDAnalyzer()
        assert analyzer.data is None
        assert analyzer.flash_info is None
        
        data = b'\xff' * 1024
        analyzer_with_data = NANDAnalyzer(data)
        assert analyzer_with_data.data == data
    
    def test_parse_id_bytes_samsung(self):
        """Test parsing Samsung NAND flash ID bytes."""
        analyzer = NANDAnalyzer()
        # Samsung K9F2G08U0M: EC D3 51 95
        id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
        
        flash_info = analyzer.parse_id_bytes(id_bytes)
        
        assert flash_info.manufacturer_id == 0xEC
        assert flash_info.device_id == 0xD3
        assert flash_info.page_size > 0
        assert flash_info.block_size > 0
        assert flash_info.total_size > 0
        assert flash_info.spare_size > 0
    
    def test_parse_id_bytes_hynix(self):
        """Test parsing Hynix NAND flash ID bytes."""
        analyzer = NANDAnalyzer()
        # Hynix HY27UF084G2B: AD DC 10 95
        id_bytes = bytes([0xAD, 0xDC, 0x10, 0x95])
        
        flash_info = analyzer.parse_id_bytes(id_bytes)
        
        assert flash_info.manufacturer_id == 0xAD
        assert flash_info.device_id == 0xDC
    
    def test_parse_id_bytes_too_short(self):
        """Test that parsing fails with too few ID bytes."""
        analyzer = NANDAnalyzer()
        id_bytes = bytes([0xEC, 0xD3])  # Only 2 bytes
        
        with pytest.raises(ValueError, match="at least 4 bytes"):
            analyzer.parse_id_bytes(id_bytes)
    
    def test_get_manufacturer_name(self):
        """Test manufacturer name lookup."""
        analyzer = NANDAnalyzer()
        
        assert analyzer.get_manufacturer_name(0xEC) == "Samsung"
        assert analyzer.get_manufacturer_name(0xAD) == "Hynix"
        assert analyzer.get_manufacturer_name(0x2C) == "Micron"
        assert "Unknown" in analyzer.get_manufacturer_name(0xFF)
    
    def test_calculate_ecc(self):
        """Test ECC calculation."""
        analyzer = NANDAnalyzer()
        
        data = b'\x00\x01\x02\x03'
        ecc = analyzer.calculate_ecc(data)
        assert isinstance(ecc, int)
        
        # ECC should be XOR of all bytes: 0x00 ^ 0x01 ^ 0x02 ^ 0x03 = 0x00
        assert ecc == 0x00
        
        data2 = b'\xFF\xFF'
        ecc2 = analyzer.calculate_ecc(data2)
        assert ecc2 == 0x00  # 0xFF ^ 0xFF = 0x00
    
    def test_verify_ecc(self):
        """Test ECC verification."""
        analyzer = NANDAnalyzer()
        
        data = b'\x01\x02\x03'
        ecc = analyzer.calculate_ecc(data)
        
        assert analyzer.verify_ecc(data, ecc) is True
        assert analyzer.verify_ecc(data, ecc + 1) is False
    
    def test_analyze_bad_blocks_no_bad_blocks(self):
        """Test bad block analysis with clean data."""
        analyzer = NANDAnalyzer()
        
        # Create data with all erased blocks (0xFF)
        data = b'\xFF' * (self.TEST_BLOCK_SIZE * 4)
        
        bad_blocks = analyzer.analyze_bad_blocks(data, self.TEST_BLOCK_SIZE)
        assert len(bad_blocks) == 0
    
    def test_analyze_bad_blocks_with_bad_blocks(self):
        """Test bad block analysis with bad blocks."""
        analyzer = NANDAnalyzer()
        
        # Create data with first block good, second block bad
        good_block = b'\xFF' * self.TEST_BLOCK_SIZE
        bad_block = b'\x00' + b'\xFF' * (self.TEST_BLOCK_SIZE - 1)
        data = good_block + bad_block
        
        bad_blocks = analyzer.analyze_bad_blocks(data, self.TEST_BLOCK_SIZE)
        assert len(bad_blocks) > 0
    
    def test_analyze_wear_leveling(self):
        """Test wear leveling analysis."""
        analyzer = NANDAnalyzer()
        
        # Create 10 pages: 5 erased, 5 written
        erased_pages = b'\xFF' * (self.TEST_PAGE_SIZE * 5)
        written_pages = b'\x00' * (self.TEST_PAGE_SIZE * 5)
        data = erased_pages + written_pages
        
        stats = analyzer.analyze_wear_leveling(data, self.TEST_PAGE_SIZE)
        
        assert stats['total_pages'] == 10
        assert stats['erased_pages'] == 5
        assert stats['written_pages'] == 5
        assert stats['utilization_percent'] == 50.0
    
    def test_generate_report_without_flash_info(self):
        """Test report generation without flash info."""
        analyzer = NANDAnalyzer()
        
        report = analyzer.generate_report()
        assert "No flash information available" in report
    
    def test_generate_report_with_flash_info(self):
        """Test report generation with flash info."""
        analyzer = NANDAnalyzer()
        id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
        analyzer.parse_id_bytes(id_bytes)
        
        report = analyzer.generate_report()
        
        assert "NAND FLASH ANALYSIS REPORT" in report
        assert "Manufacturer ID" in report
        assert "Device ID" in report
        assert "Samsung" in report
    
    def test_generate_report_with_data(self):
        """Test report generation with data analysis."""
        data = b'\xFF' * (self.TEST_BLOCK_SIZE * 2)
        
        analyzer = NANDAnalyzer(data)
        id_bytes = bytes([0xEC, 0xD3, 0x51, 0x95])
        analyzer.parse_id_bytes(id_bytes)
        
        report = analyzer.generate_report()
        
        assert "Data Analysis" in report
        assert "Wear Leveling Statistics" in report
        assert "Utilization" in report
    
    def test_flash_info_str(self):
        """Test NANDFlashInfo string representation."""
        flash_info = NANDFlashInfo(
            manufacturer_id=0xEC,
            device_id=0xD3,
            page_size=2048,
            block_size=128 * 1024,
            total_size=256 * 1024 * 1024,
            spare_size=64
        )
        
        info_str = str(flash_info)
        assert "0xEC" in info_str
        assert "0xD3" in info_str
        assert "2048" in info_str
        assert "MB" in info_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
