"""
SDF-QPUMP Core Infrastructure Module
Author: Adel Gachkar
Version: 0.1.0
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__version__ = "0.1.0"
__author__ = "Adel Gachkar"

# صادر کردن اجزای گراف و محاسبات هسته
try:
    from .graph import Graph, ComputationalGraph
    __all__ = ["Graph", "ComputationalGraph"]
except ImportError as e:
    # در صورتی که فایل graph به صورت مجزا صدا زده شود
    try:
        from core.graph import Graph, ComputationalGraph
        __all__ = ["Graph", "ComputationalGraph"]
    except ImportError as inner_e:
        logger.warning(f"Could not load core Graph components: {inner_e}")
        __all__ = []
