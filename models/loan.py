from odoo import models, fields, api
from datetime import timedelta, date

class LoanRequest(models.Model):
    _name = 'loan.request'
    _description = 'Solicitud de Préstamo'

    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    amount = fields.Float(string='Monto Solicitado', required=True)
    term_days = fields.Integer(string='Plazo (días)', required=True)
    interest_rate = fields.Float(string='Tasa de Interés (%)', required=True, default=10.0)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft')

    def approve_loan(self):
        """Aprobar préstamo y crear el préstamo asociado."""
        for request in self:
            loan_vals = {
                'partner_id': request.partner_id.id,
                'amount': request.amount,
                'interest_rate': request.interest_rate,
                'total_amount': request.amount * (1 + request.interest_rate / 100),
                'daily_payment': (request.amount * (1 + request.interest_rate / 100)) / request.term_days,
                'due_date': date.today() + timedelta(days=request.term_days),
                'state': 'active'
            }
            self.env['loan.loan'].create(loan_vals)
            request.state = 'approved'

class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Préstamo'

    name = fields.Char(string="Identificador de prestamo")
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    amount = fields.Float(string='Monto Original', required=True)
    interest_rate = fields.Float(string='Tasa de Interés (%)', required=True)
    total_amount = fields.Float(string='Total a Pagar', compute='_compute_total_amount', store=True)
    daily_payment = fields.Float(string='Monto a Pagar por Día', required=True)
    due_date = fields.Date(string='Fecha de Vencimiento', required=True)
    balance = fields.Float(string='Saldo Pendiente', compute='_compute_balance', store=True)
    state = fields.Selection([
        ('active', 'Activo'),
        ('paid', 'Pagado'),
        ('overdue', 'En Mora')
    ], string='Estado', default='active')

    @api.depends('amount', 'interest_rate')
    def _compute_total_amount(self):
        for loan in self:
            loan.total_amount = loan.amount * (1 + loan.interest_rate / 100)

    @api.depends('total_amount', 'payment_ids.amount')
    def _compute_balance(self):
        for loan in self:
            total_paid = sum(loan.payment_ids.mapped('amount'))
            loan.balance = loan.total_amount - total_paid
            if loan.balance <= 0:
                loan.state = 'paid'
            elif date.today() > loan.due_date:
                loan.state = 'overdue'

    payment_ids = fields.One2many('loan.payment', 'loan_id', string='Pagos')

class LoanPayment(models.Model):
    _name = 'loan.payment'
    _description = 'Pago de Préstamo'

    loan_id = fields.Many2one('loan.loan', string='Préstamo', required=True)
    date = fields.Date(string='Fecha de Pago', default=fields.Date.today, required=True)
    amount = fields.Float(string='Monto Pagado', required=True)

    def register_payment(self):
        """Registra un pago y actualiza el estado del préstamo."""
        for payment in self:
            loan = payment.loan_id
            loan.balance -= payment.amount
            if loan.balance <= 0:
                loan.state = 'paid'
