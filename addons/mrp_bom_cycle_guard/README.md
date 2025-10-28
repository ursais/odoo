# MRP BOM Cycle Guard

## Overview

This module prevents 504 Gateway Timeout errors that occur during BOM (Bill of Materials) 
explosion when there are circular dependencies in the BOM structure.

## Problem Statement

The Damage Control QA server was experiencing 504 Gateway Timeout errors when running 
the Scheduler. This was caused by infinite loops in BOM computation due to circular 
dependencies, where a product's BOM references itself either directly or indirectly 
through a chain of components.

## Solution

This module enhances the core `mrp.bom` model's `explode()` method with:

### 1. Recursion Depth Tracking
- Implements a maximum recursion depth limit (default: 100 levels)
- Tracks the current depth during BOM explosion
- Raises clear error when depth is exceeded

### 2. Enhanced Cycle Detection
- Maintains a visited products set for early cycle detection
- Uses DFS (Depth-First Search) algorithm for graph cycle detection
- Checks for cycles before processing each sub-BOM

### 3. Improved Error Reporting
- Provides detailed error messages showing the exact product chain causing the cycle
- Logs debug information for troubleshooting
- Helps administrators quickly identify and fix problematic BOMs

### 4. Performance Optimization
- Early cycle detection prevents unnecessary processing
- Efficient graph traversal algorithms
- Minimal overhead for non-problematic BOMs

## Technical Details

### Key Features

- **Inherits from**: `mrp.bom`
- **Overrides**: `explode()` method
- **Maximum Recursion Depth**: 100 (configurable via `MAX_RECURSION_DEPTH` constant)

### Algorithm Improvements

1. **Product Chain Tracking**: Each iteration maintains a chain of products from root to current
2. **Visited Products Set**: Fast O(1) lookup to detect when a product appears twice
3. **Depth Counter**: Prevents stack overflow and excessive processing
4. **Graph-based Cycle Detection**: DFS algorithm with recursion stack tracking

## Installation

1. Copy the module to your Odoo addons directory
2. Update the module list: `Settings > Apps > Update Apps List`
3. Search for "MRP BOM Cycle Guard"
4. Click Install

## Usage

Once installed, the module automatically enhances all BOM explosions system-wide:

- No configuration required
- Works transparently with existing BOMs
- Scheduler will no longer timeout on circular BOMs
- Clear error messages guide users to fix problematic BOMs

## Error Messages

When a circular dependency is detected, users will see:

```
Circular dependency detected in Bill of Materials!

Product 'Product A' references itself in its BOM structure.

Product chain:
Product A -> Product B -> Product C -> Product A

Please review your BOM configuration and remove the circular reference.
```

## Logging

The module logs detailed information for debugging:

- Start of BOM explosion with product and quantity
- Maximum recursion depth reached
- Number of BOMs and lines processed
- Error details when cycles are detected

View logs in: `Settings > Technical > Logging`

## Configuration

To adjust the maximum recursion depth, edit the `MAX_RECURSION_DEPTH` constant 
in `models/mrp_bom.py`:

```python
class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    # Adjust this value if needed
    MAX_RECURSION_DEPTH = 100  # Default: 100 levels
```

## Compatibility

- **Odoo Version**: 16.0
- **Dependencies**: `mrp` module
- **Database**: No database changes required

## Support

For issues or questions, contact the Damage Control QA team.

## License

LGPL-3.0 or later
