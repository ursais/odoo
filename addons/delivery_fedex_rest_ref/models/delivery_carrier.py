# -*- coding: utf-8 -*-
import json
import logging
import threading
from functools import wraps

from odoo import api, models

_logger = logging.getLogger(__name__)

# Thread-local storage for passing customer references into the HTTP layer
_local = threading.local()

# Lock to serialize Session.request patching across threads
_patch_lock = threading.Lock()

# Maximum length for FedEx reference values
FEDEX_REF_MAX_LENGTH = 35


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _get_fedex_rest_customer_references(self, picking):
        """Build the customerReferences list for the FedEx REST Ship API.

        FedEx supports up to 3 customer reference types per package:
        - CUSTOMER_REFERENCE: General customer reference (SO name / picking origin)
        - P_O_NUMBER: Purchase Order number (client_order_ref on the sale order)
        - INVOICE_NUMBER: Invoice number (sale order name if different from origin)

        Each value is truncated to 35 characters per FedEx API constraints.

        :param picking: stock.picking record
        :return: list of dicts with customerReferenceType and value keys
        """
        references = []
        sale_order = picking.sale_id

        # CUSTOMER_REFERENCE: picking origin typically holds the SO name
        origin = picking.origin or ''
        if origin:
            references.append({
                'customerReferenceType': 'CUSTOMER_REFERENCE',
                'value': origin[:FEDEX_REF_MAX_LENGTH],
            })

        # P_O_NUMBER: the customer's own PO reference
        if sale_order and sale_order.client_order_ref:
            references.append({
                'customerReferenceType': 'P_O_NUMBER',
                'value': sale_order.client_order_ref[:FEDEX_REF_MAX_LENGTH],
            })

        # INVOICE_NUMBER: use the sale order name when distinct from origin
        if sale_order and sale_order.name and sale_order.name != origin:
            references.append({
                'customerReferenceType': 'INVOICE_NUMBER',
                'value': sale_order.name[:FEDEX_REF_MAX_LENGTH],
            })

        return references

    def _inject_refs_into_fedex_body(self, body, references):
        """Inject customerReferences into a FedEx REST API request body.

        Modifies the body dict in-place, adding references to each
        requestedPackageLineItem that doesn't already have them.

        :param body: dict representing the JSON body of the FedEx ship request
        :param references: list of reference dicts to inject
        """
        if not references or not isinstance(body, dict):
            return

        shipment = body.get('requestedShipment', {})
        items = shipment.get('requestedPackageLineItems', [])
        for item in items:
            if isinstance(item, dict) and 'customerReferences' not in item:
                item['customerReferences'] = references

    def fedex_rest_send_shipping(self, pickings):
        """Override to inject customer references into FedEx REST label requests.

        Uses thread-local storage to pass reference data into the HTTP request
        layer, ensuring the FedEx Ship API payload includes customerReferences
        in each requestedPackageLineItem.
        """
        # Collect references from the picking(s)
        all_references = []
        for picking in pickings:
            refs = self._get_fedex_rest_customer_references(picking)
            if refs:
                all_references = refs
                if self.debug_logging:
                    _logger.info(
                        "FedEx REST refs for picking %s: %s",
                        picking.name, refs
                    )
                break

        if not all_references:
            return super().fedex_rest_send_shipping(pickings)

        # Store references in thread-local so the patched request can access them
        _local.fedex_customer_references = all_references
        _local.carrier_instance = self

        try:
            return self._fedex_rest_send_with_references(pickings)
        finally:
            _local.fedex_customer_references = None
            _local.carrier_instance = None

    def _fedex_rest_send_with_references(self, pickings):
        """Execute the parent send_shipping with HTTP interception active.

        Patches requests.Session.request to intercept FedEx Ship API calls
        and inject customer references into the JSON body. Uses a lock to
        ensure thread safety when multiple threads send shipments concurrently.
        """
        import requests as req_lib

        with _patch_lock:
            original_request = req_lib.Session.request

            @wraps(original_request)
            def patched_request(session_self, method, url, **kwargs):
                refs = getattr(_local, 'fedex_customer_references', None)
                carrier = getattr(_local, 'carrier_instance', None)

                if (refs and carrier and method.upper() == 'POST'
                        and self._is_fedex_ship_url(url)):
                    body = kwargs.get('json')
                    if body is not None:
                        carrier._inject_refs_into_fedex_body(body, refs)
                    elif 'data' in kwargs and kwargs['data']:
                        try:
                            body = json.loads(kwargs['data'])
                            carrier._inject_refs_into_fedex_body(body, refs)
                            kwargs['data'] = json.dumps(body)
                        except (json.JSONDecodeError, TypeError):
                            pass

                return original_request(session_self, method, url, **kwargs)

            req_lib.Session.request = patched_request
            try:
                return super().fedex_rest_send_shipping(pickings)
            finally:
                req_lib.Session.request = original_request

    @api.model
    def _is_fedex_ship_url(self, url):
        """Check if a URL is a FedEx Ship API endpoint.

        Matches both sandbox and production FedEx Ship API URLs:
        - https://apis-sandbox.fedex.com/ship/v1/shipments
        - https://apis.fedex.com/ship/v1/shipments
        """
        if not url:
            return False
        url_lower = url.lower()
        return ('fedex.com' in url_lower and '/ship/' in url_lower)
