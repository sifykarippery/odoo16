from odoo import fields, models, api


class AnalyticBudgetInherit(models.Model):
    _inherit = 'crossovered.budget.lines'

    analytic_tag_id = fields.Many2one('account.analytic.tag','Analytic Tag')

    def _compute_practical_amount(self):
        res=super(AnalyticBudgetInherit,self)._compute_practical_amount()
        for line in self:
            if line.analytic_tag_id.id:
                acc_mov_lin_obj = self.env['account.move.line']
                domain = [('analytic_exp_center_id', 'in',
                           line.analytic_tag_id.ids),
                          ('date', '>=', line.date_from),
                          ('date', '<=', line.date_to),
                          ('move_id.state', '=', 'posted')
                          ]
                where_query = acc_mov_lin_obj._where_calc(domain)
                acc_mov_lin_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause
                self.env.cr.execute(select, where_clause_params)
                line.practical_amount = self.env.cr.fetchone()[0] or 0.0
            else:
                pass
        return res

    def _compute_percentage(self):
        res=super(AnalyticBudgetInherit,self)._compute_percentage()
        for line in self:
            if line.analytic_tag_id.id:
                if line.planned_amount != 0.00:
                    line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
                else:
                    line.percentage = 0.00
        return res