# -*- coding: utf-8 -*-
"""
Stop Name Encoder/Decoder Module
Handles the encoding and decoding of bus stop names with special prefixes and suffixes.

Prefix Rules:
- '_': Auto-play
- '!': Chinese has 1 page turn (2 pages total)
- '!!': Chinese has 2 page turns (3 pages total)
- '_!': Auto-play + 1 page turn (2 pages)
- '_!!': Auto-play + 2 page turns (3 pages)
- '~': 6w has 1 page turn (2 pages), 8w no turn (1 page)
- '!~': 6w has 2 page turns (3 pages), 8w has 1 turn (2 pages)
- '_~': Auto-play + 6w 1 turn, 8w no turn
- '_!~': Auto-play + 6w 2 turns, 8w 1 turn

Suffix Rules:
- '!': 3/4 line English (engdisp has >= 2 '@' symbols, count('@') > 2)
"""

import re
from typing import Tuple, Dict, Any


class StopNameProperties:
    """Class to hold the properties extracted from or to be encoded into a stop name."""
    
    def __init__(self):
        self.autoskip: bool = False
        self.w8w6_different: bool = False  # True if 8w and 6w have different pages
        self.chi_pages: int = 1  # 1-3 pages
        self.eng_multiline: bool = False  # True if English has 3+ lines
        self.base_name: str = ""  # The actual name without prefix/suffix
        

def decode_stop_name(stop_name: str) -> StopNameProperties:
    """
    Parse a stop name and extract its properties from prefixes and suffixes.
    
    Args:
        stop_name: The complete stop name with prefixes/suffixes
        
    Returns:
        StopNameProperties object with extracted properties
    """
    props = StopNameProperties()
    
    # Work with a copy
    name = stop_name
    
    # Check for suffix '!' (3/4 line English)
    if name.endswith('!'):
        props.eng_multiline = True
        name = name[:-1]
    
    # Check for prefixes (order matters - check longest first)
    if name.startswith('_!~'):
        props.autoskip = True
        props.w8w6_different = True
        props.chi_pages = 3  # For 8w: 2 pages, for 6w: 3 pages
        name = name[3:]
    elif name.startswith('_~'):
        props.autoskip = True
        props.w8w6_different = True
        props.chi_pages = 2  # For 8w: 1 page, for 6w: 2 pages
        name = name[2:]
    elif name.startswith('_!!'):
        props.autoskip = True
        props.chi_pages = 3
        name = name[3:]
    elif name.startswith('_!'):
        props.autoskip = True
        props.chi_pages = 2
        name = name[2:]
    elif name.startswith('!~'):
        props.w8w6_different = True
        props.chi_pages = 3  # For 8w: 2 pages, for 6w: 3 pages
        name = name[2:]
    elif name.startswith('~'):
        props.w8w6_different = True
        props.chi_pages = 2  # For 8w: 1 page, for 6w: 2 pages
        name = name[1:]
    elif name.startswith('!!'):
        props.chi_pages = 3
        name = name[2:]
    elif name.startswith('!'):
        props.chi_pages = 2
        name = name[1:]
    elif name.startswith('_'):
        props.autoskip = True
        name = name[1:]
    
    props.base_name = name
    return props


def encode_stop_name(base_name: str, autoskip: bool, w8w6_different: bool, 
                     chi_pages: int, eng_at_count: int) -> str:
    """
    Encode a stop name with the appropriate prefixes and suffixes based on properties.
    
    Args:
        base_name: The base name without any prefix/suffix
        autoskip: Whether autoskip is enabled
        w8w6_different: Whether 8w and 6w have different pages
        chi_pages: Number of Chinese pages (1-3)
        eng_at_count: Count of '@' symbols in English display
        
    Returns:
        The encoded stop name with appropriate prefixes and suffixes
    """
    # Start with base name
    name = base_name
    
    # Determine prefix based on properties
    prefix = ""
    
    if w8w6_different:
        # Handle 8w6w different cases
        # Note: chi_pages here represents the 8w page count
        # 6w will have chi_pages + 1
        if chi_pages == 2:
            prefix = "~"  # 8w: 1 page, 6w: 2 pages (1 turn)
        elif chi_pages == 3:
            prefix = "!~"  # 8w: 2 pages (1 turn), 6w: 3 pages (2 turns)
        
        if autoskip:
            prefix = "_" + prefix
    else:
        # Handle normal page cases
        if chi_pages == 2:
            prefix = "!"
        elif chi_pages == 3:
            prefix = "!!"
        
        if autoskip:
            prefix = "_" + prefix
            if prefix == "_":  # If only autoskip
                prefix = "_"
    
    # Check for English multiline suffix
    suffix = ""
    if eng_at_count > 2:
        suffix = "!"
    
    return prefix + name + suffix


def update_stop_name_from_ui(current_name: str, autoskip: bool, w8w6_different: bool,
                              chi_pages: int, eng_display: str) -> str:
    """
    Update a stop name based on UI field values.
    
    Args:
        current_name: Current stop name (may have prefixes/suffixes)
        autoskip: Autoskip checkbox value
        w8w6_different: 8w6w checkbox value
        chi_pages: Chinese pages spinbox value (1-3)
        eng_display: English display text (to count '@')
        
    Returns:
        Updated stop name with appropriate prefixes/suffixes
    """
    # Decode current name to get base name
    props = decode_stop_name(current_name)
    
    # Count '@' in English display
    eng_at_count = eng_display.count('@')
    
    # Encode with new properties
    return encode_stop_name(props.base_name, autoskip, w8w6_different, 
                           chi_pages, eng_at_count)


def get_ui_values_from_name(stop_name: str, eng_display: str = "") -> Dict[str, Any]:
    """
    Get UI field values from a stop name.
    
    Args:
        stop_name: The stop name with prefixes/suffixes
        eng_display: English display text (to verify multiline)
        
    Returns:
        Dictionary with UI field values:
        - 'autoskip': bool
        - 'w8w6_different': bool
        - 'chi_pages': int (1-3)
    """
    props = decode_stop_name(stop_name)
    
    return {
        'autoskip': props.autoskip,
        'w8w6_different': props.w8w6_different,
        'chi_pages': props.chi_pages,
        'base_name': props.base_name
    }
