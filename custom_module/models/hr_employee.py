

from odoo import models, fields, api,exceptions,_


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    # //Update function with the project details argument
    def attendance_manual_inherit(self, next_action,dict,entered_pin=None):

        self.ensure_one()
        attendance_user_and_no_pin = self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        can_check_without_pin = attendance_user_and_no_pin or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_action_inherit(next_action,dict)
        if not self.user_has_groups('hr_attendance.group_hr_attendance_user'):
            return {'warning': _(
                'To activate Kiosk mode without pin code, you must have access right as an Officer or above in the Attendance app. Please contact your administrator.')}
        return {'warning': _('Wrong PIN')}
    def _attendance_action_inherit(self, next_action,dict):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today
        action_message['kiosk_delay'] = employee.company_id.attendance_kiosk_delay * 1000

        if employee.user_id:
            modified_attendance = employee.with_user(employee.user_id).sudo()._attendance_action_change_inherit(dict)
        else:
            modified_attendance = employee._attendance_action_change_inherit(dict)
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime
        # Overtime have an unique constraint on the day, no need for limit=1
        action_message['overtime_today'] = self.env['hr.attendance.overtime'].sudo().search([
            ('employee_id', '=', employee.id), ('date', '=', fields.Date.context_today(self)), ('adjustment', '=', False)]).duration or 0
        return {'action': action_message}

    @api.model
    def _attendance_action_change_inherit(self, dict):
        """
        Check In/Check Out action:
        - Check In: create a new attendance record
        - Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()

        # Check if project and task values are provided
        if not (dict.get('project_value') and dict.get('task_value')):
            raise exceptions.UserError("Fill the Project and Task ")

        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            # Create a new attendance record for Check In
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'project_id': int(dict.get('project_value')),
                'task_id': int(dict.get('task_value')),
                'description': dict.get('description_value')
            }
            return self.env['hr.attendance'].create(vals)

        # Find the corresponding Check In attendance record for Check Out
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.id),
            ('check_out', '=', False)
        ], limit=1)

        if attendance:
            # Modify check_out field for Check Out correct project and task
            if attendance.project_id.id == int(dict.get('project_value')) and(
                    attendance.task_id.id == int(dict.get('task_value'))):
                attendance.check_out = action_date
            else:
                raise exceptions.UserError("Select your Project and Task Correctly")
        else:
            raise exceptions.UserError(
                _('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                  'Your attendances have probably been modified manually by human resources.') %
                {'empl_name': self.sudo().name, }
            )

        return attendance