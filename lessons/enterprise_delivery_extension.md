# Odoo Enterprise Module Extension Patterns

## Extending enterprise delivery modules without source access

When an enterprise module (like `delivery_fedex_rest`) isn't available in the repo:

1. The delivery framework uses `delivery_type` selection field and dispatches via
   `getattr(self, '%s_send_shipping' % self.delivery_type)(pickings)`
2. Enterprise modules add their own `delivery_type` and corresponding methods
3. `DeliveryPackage` objects from `_get_packages_from_picking` carry `picking_id` and `order_id`
4. `stock.picking` has `sale_id` (via sale_stock), `origin` (SO name), and related fields

## FedEx REST API reference info

- Ship endpoint: `https://apis.fedex.com/ship/v1/shipments` (prod) or `apis-sandbox.fedex.com`
- `customerReferences` go inside each `requestedPackageLineItems` entry
- Max 3 refs: CUSTOMER_REFERENCE, P_O_NUMBER, INVOICE_NUMBER
- Max value length: 35 chars

## HTTP interception pattern for enterprise module extension

When you can't override a helper class method (because it's not an Odoo model),
you can use `requests.Session.request` monkey-patching with thread-local storage
and a threading lock for safety. This works because all `requests.get/post/etc`
and `session.get/post/etc` calls ultimately go through `Session.request`.
