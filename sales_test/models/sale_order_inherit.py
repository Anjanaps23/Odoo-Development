from odoo import models


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        for order in self:
            order.write({'picking_ids': [(5, 0, 0)]})
            for line in order.order_line:
                delivery = self.env['stock.picking'].create({
                    'partner_id': order.partner_shipping_id.id,
                    'picking_type_id': order.warehouse_id.out_type_id.id,
                    'sale_id': order.id,
                    'move_ids_without_package': [(0, 0, {
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': line.product_id.property_stock_production.id,
                        'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
                        'origin': order.name,
                        'sale_line_id': line.id,
                    })]
                })
                order.send_delivery_email_notification(delivery.scheduled_date)
        return res

    def send_delivery_email_notification(self, date):
        for rec in self:
            mail = self.env['mail.mail'].sudo().create({
                'subject': 'Delivery status',
                'email_to': rec.partner_id.email,
                'email_from': rec.company_id.email,
                'body_html': """<div>
                                <p>Hi """ + ' ' + str(rec.partner_id.name) + """,</p>
                                 <p>The status of the delivery of your order is as follows:</p>
                                <p>Delivery status: """ + str(rec.delivery_status) + """</p>
                                <p>Expected delivery: """ + str(date) + """</p>

                                <br/>
                           </div>"""

            })
            mail.send()


