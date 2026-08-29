# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from collections import defaultdict

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    """
    Inherit mrp.bom to add enhanced cycle detection and recursion protection
    to prevent 504 Gateway Timeout errors during BOM explosion.
    """
    _inherit = 'mrp.bom'

    # Maximum recursion depth to prevent infinite loops
    MAX_RECURSION_DEPTH = 100

    def explode(self, product, quantity, picking_type=False):
        """
        Override the explode method to add robust recursion guards and cycle detection.
        
        This enhanced version prevents infinite loops by:
        1. Tracking recursion depth with a configurable maximum
        2. Maintaining a visited products set to detect cycles early
        3. Implementing efficient cycle detection before processing
        4. Providing clear error messages when issues are detected
        
        :param product: Product to explode
        :param quantity: Quantity to produce
        :param picking_type: Picking type (optional)
        :return: Tuple of (boms_done, lines_done)
        :raises UserError: When circular dependency or excessive recursion is detected
        """
        _logger.debug(
            "Starting BOM explosion for product '%s' (ID: %s) with quantity %s",
            product.display_name, product.id, quantity
        )
        
        # Initialize graph structures for cycle detection
        graph = defaultdict(list)
        V = set()
        
        # Track recursion depth to prevent excessive nesting
        recursion_tracker = {'depth': 0, 'max_depth_reached': 0}
        
        # Track visited products to detect cycles
        visited_products = set()
        
        def check_cycle(v, visited, recStack, graph):
            """
            Detect cycles in the BOM graph using DFS algorithm.
            
            :param v: Current vertex (product template ID)
            :param visited: Dictionary of visited vertices
            :param recStack: Dictionary tracking recursion stack
            :param graph: Graph structure (adjacency list)
            :return: True if cycle detected, False otherwise
            """
            visited[v] = True
            recStack[v] = True
            
            for neighbour in graph[v]:
                if not visited.get(neighbour, False):
                    if check_cycle(neighbour, visited, recStack, graph):
                        return True
                elif recStack.get(neighbour, False):
                    return True
            
            recStack[v] = False
            return False
        
        def check_recursion_depth(current_depth, product_chain):
            """
            Check if recursion depth exceeds maximum allowed.
            
            :param current_depth: Current recursion depth
            :param product_chain: Chain of products leading to current depth
            :raises UserError: If depth exceeds maximum
            """
            if current_depth > self.MAX_RECURSION_DEPTH:
                chain_names = ' -> '.join([p.display_name for p in product_chain])
                _logger.error(
                    "Maximum recursion depth (%s) exceeded during BOM explosion. "
                    "Product chain: %s",
                    self.MAX_RECURSION_DEPTH, chain_names
                )
                raise UserError(_(
                    "BOM explosion exceeded maximum recursion depth of %s levels.\n\n"
                    "This indicates a circular dependency in the Bill of Materials.\n\n"
                    "Product chain:\n%s\n\n"
                    "Please check your BOM configuration and remove any circular references."
                ) % (self.MAX_RECURSION_DEPTH, chain_names))
        
        # Initialize data structures
        product_ids = set()
        product_boms = {}
        
        def update_product_boms():
            """Update the product_boms cache with BOMs for pending products."""
            products = self.env['product.product'].browse(product_ids)
            product_boms.update(
                self._bom_find(
                    products,
                    picking_type=picking_type or self.picking_type_id,
                    company_id=self.company_id.id,
                    bom_type='phantom'
                )
            )
            # Set missing keys to default value
            for prod in products:
                product_boms.setdefault(prod, self.env['mrp.bom'])
        
        # Initialize result lists
        boms_done = [(
            self,
            {
                'qty': quantity,
                'product': product,
                'original_qty': quantity,
                'parent_line': False
            }
        )]
        lines_done = []
        
        # Add initial product to visited set
        V.add(product.product_tmpl_id.id)
        visited_products.add(product.id)
        
        # Initialize BOM lines queue with product chain tracking
        bom_lines = []
        for bom_line in self.bom_line_ids:
            product_id = bom_line.product_id
            V.add(product_id.product_tmpl_id.id)
            graph[product.product_tmpl_id.id].append(product_id.product_tmpl_id.id)
            bom_lines.append((
                bom_line,
                product,
                quantity,
                False,
                [product],  # Product chain for recursion tracking
                1  # Recursion depth
            ))
            product_ids.add(product_id.id)
        
        # Initial BOM fetch
        update_product_boms()
        product_ids.clear()
        
        # Process BOM lines queue
        while bom_lines:
            current_line, current_product, current_qty, parent_line, product_chain, depth = bom_lines[0]
            bom_lines = bom_lines[1:]
            
            # Update max depth tracking
            recursion_tracker['max_depth_reached'] = max(
                recursion_tracker['max_depth_reached'],
                depth
            )
            
            # Check recursion depth
            check_recursion_depth(depth, product_chain)
            
            # Skip line if not applicable to current product variant
            if current_line._skip_bom_line(current_product):
                continue
            
            # Calculate line quantity
            line_quantity = current_qty * current_line.product_qty
            
            # Ensure BOM is in cache
            if current_line.product_id not in product_boms:
                product_ids.add(current_line.product_id.id)
                update_product_boms()
                product_ids.clear()
            
            bom = product_boms.get(current_line.product_id)
            
            if bom:
                # Check for cycle before processing sub-BOM
                current_tmpl_id = current_line.product_id.product_tmpl_id.id
                
                # Early cycle detection: check if product already in chain
                if current_line.product_id in visited_products:
                    chain_names = ' -> '.join([p.display_name for p in product_chain])
                    chain_names += ' -> ' + current_line.product_id.display_name
                    _logger.error(
                        "Circular dependency detected in BOM. Product '%s' (ID: %s) "
                        "appears multiple times in the chain: %s",
                        current_line.product_id.display_name,
                        current_line.product_id.id,
                        chain_names
                    )
                    raise UserError(_(
                        "Circular dependency detected in Bill of Materials!\n\n"
                        "Product '%s' references itself in its BOM structure.\n\n"
                        "Product chain:\n%s\n\n"
                        "Please review your BOM configuration and remove the circular reference."
                    ) % (current_line.product_id.display_name, chain_names))
                
                # Add to visited products
                visited_products.add(current_line.product_id)
                
                # Calculate converted quantity
                converted_line_quantity = current_line.product_uom_id._compute_quantity(
                    line_quantity / bom.product_qty,
                    bom.product_uom_id
                )
                
                # Add sub-BOM lines to queue with updated chain and depth
                new_chain = product_chain + [current_line.product_id]
                new_depth = depth + 1
                
                for bom_line in bom.bom_line_ids:
                    graph[current_tmpl_id].append(bom_line.product_id.product_tmpl_id.id)
                    
                    # Enhanced cycle check
                    if bom_line.product_id.product_tmpl_id.id in V:
                        visited_dict = {key: False for key in V}
                        rec_stack = {key: False for key in V}
                        if check_cycle(bom_line.product_id.product_tmpl_id.id, visited_dict, rec_stack, graph):
                            chain_names = ' -> '.join([p.display_name for p in new_chain])
                            chain_names += ' -> ' + bom_line.product_id.display_name
                            _logger.error(
                                "Recursion cycle detected for product '%s' (ID: %s). Chain: %s",
                                bom_line.product_id.display_name,
                                bom_line.product_id.id,
                                chain_names
                            )
                            raise UserError(_(
                                "Recursion error! A product with a Bill of Materials should not "
                                "have itself in its BOM or child BOMs!\n\n"
                                "Circular reference detected:\n%s\n\n"
                                "Please correct the BOM configuration to remove this circular dependency."
                            ) % chain_names)
                    
                    V.add(bom_line.product_id.product_tmpl_id.id)
                    
                    if bom_line.product_id not in product_boms:
                        product_ids.add(bom_line.product_id.id)
                    
                    bom_lines.append((
                        bom_line,
                        current_line.product_id,
                        converted_line_quantity,
                        current_line,
                        new_chain,
                        new_depth
                    ))
                
                # Add to results
                boms_done.append((
                    bom,
                    {
                        'qty': converted_line_quantity,
                        'product': current_product,
                        'original_qty': quantity,
                        'parent_line': current_line
                    }
                ))
            else:
                # No sub-BOM: add as final line
                rounding = current_line.product_uom_id.rounding
                line_quantity = float_round(
                    line_quantity,
                    precision_rounding=rounding,
                    rounding_method='UP'
                )
                lines_done.append((
                    current_line,
                    {
                        'qty': line_quantity,
                        'product': current_product,
                        'original_qty': quantity,
                        'parent_line': parent_line
                    }
                ))
        
        _logger.debug(
            "BOM explosion completed for product '%s'. Max depth reached: %s, "
            "BOMs processed: %s, Lines processed: %s",
            product.display_name,
            recursion_tracker['max_depth_reached'],
            len(boms_done),
            len(lines_done)
        )
        
        return boms_done, lines_done
