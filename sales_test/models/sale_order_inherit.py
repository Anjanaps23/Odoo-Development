from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.picking_ids.unlink()
            order_lines = order.order_line
            num_deliveries = len(order_lines)

            for i in range(num_deliveries):
                delivery = self.env['stock.picking'].create({
                    'partner_id': order.partner_shipping_id.id,
                    'picking_type_id': order.warehouse_id.out_type_id.id,
                })
                self.env['stock.move'].create({
                    'name': order_lines[i].product_id.name,
                    'product_id': order_lines[i].product_id.id,
                    'product_uom': order_lines[i].product_uom.id,
                    'product_uom_qty': order_lines[i].product_uom_qty,
                    'picking_id': delivery.id,
                    'location_id': order_lines[i].order_id.warehouse_id.lot_stock_id.id,
                    'location_dest_id': order_lines[i].order_id.partner_shipping_id.property_stock_customer.id,
                })
                order.send_delivery_email_notification()
        return res

    def send_delivery_email_notification(self):
        for rec in self:
            mail = self.env['mail.mail'].sudo().create({
                'subject': 'Delivery status',
                'email_to': rec.partner_id.email,
                'email_from': rec.company_id.email,
                'body_html': """<div>
                                <p>Hi """ + ' ' + str(rec.partner_id.name) + """,</p>
                                 <p>The status of the delivery of your order is as follows:</p>
                                <p>Delivery status: """ + str(rec.delivery_status) + """</p>
                                <p>Expected delivery: """ + str(rec.expected_date) + """</p>
    
                                <br/>
                           </div>"""

            })
            mail.send()


