# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions,_


class HrAttendanceInherit(models.Model):
    _inherit = "hr.attendance"

    project_id = fields.Many2one('project.project', string='project')
    task_id = fields.Many2one('project.task',string='task')
    description=fields.Text(string='description')



