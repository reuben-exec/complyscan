"""Document parsing utilities."""
import re
from typing import Optional


class DocumentParser:
    """Parse extracted text for structured fields."""
    
    def __init__(self, text: str):
        self.text = text
        self.text_lower = text.lower()
    
    def extract_dates(self) -> list[str]:
        """Extract dates from document text."""
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # DD/MM/YYYY
            r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}",
            r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}",
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            dates.extend(matches)
        return dates
    
    def extract_signatures(self) -> list[str]:
        """Extract signature indicators from text."""
        signature_patterns = [
            r"(approved by|authorized by|signed by)[:\s]*(.+?)(?:\n|$)",
            r"(medical director|head of department|quality head)[:\s]*(.+?)(?:\n|$)",
        ]
        
        signatures = []
        for pattern in signature_patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            signatures.extend([m[1].strip() for m in matches])
        return signatures
    
    def find_section(self, section_name: str) -> Optional[str]:
        """Find a specific section in the document."""
        pattern = rf"(?:section|chapter)?\s*[\d.]+\s*{re.escape(section_name)}[^\n]*\n(.*?)(?=\n(?:section|chapter)?\s*[\d.]+|$)", re.DOTALL
        match = re.search(pattern, self.text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def contains_keywords(self, keywords: list[str]) -> dict[str, bool]:
        """Check which keywords are present in the document."""
        return {kw: kw.lower() in self.text_lower for kw in keywords}