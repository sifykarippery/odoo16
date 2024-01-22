odoo.define('custom_module.my_attendances', function (require) {
    "use strict";

    const session = require('web.session');
    const core = require('web.core');
    const MyAttendances = require('hr_attendance.my_attendances');

    MyAttendances.include({
        // Updating events for on change selecting project
        events: {
            "click .o_hr_attendance_sign_in_out_icon": _.debounce(function() {
            //update with new custom function
                this.update_attendance_project();
            }, 200, true),
            'change #projectselect': 'task_domain_change'
        },

        willStart: function () {
            var self = this;

            // Fetch project data using RPC
            var def = this._rpc({
                model: 'project.project',
                method: 'search_read',
                args: [[], ['name']],
            }).then(function (res) {
                // Store the fetched project data
                self.project_id = res;
            });

            return Promise.all([def, this._super.apply(this, arguments)]);
        },

        // Custom method to update attendance based on project
        update_attendance_project: function () {
            var self = this;
            var project_value = document.getElementById("projectselect").value;
            var task_value = document.getElementById("taskselect").value;
            var description_value = document.getElementById("description").value;

            // Prepare data for the RPC call
            var dict = {
                "project_value": project_value,
                "task_value": task_value,
                "description_value": description_value
            };

            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual_inherit',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances', dict],
                context: session.user_context,
            }).then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.displayNotification({ title: result.warning, type: 'danger' });
                }
            });
        },

        // Custom method to handle task selection change
        task_domain_change: function () {
            var selectField = this.$('#taskselect');
            var project = parseInt(document.getElementById("projectselect").value);

            // Check if a project is selected
            if (project === '') {
             return;
            }

            var self = this;

            // Perform RPC call to fetch tasks based on selected project
            var def = this._rpc({
                model: 'project.task',
                method: 'search_read',
                args: [[['project_id', '=', project]], ['name']],
            }).then(function (res) {
                // Update the task selection field options
                self.updateSelectFieldOptions(selectField, res);
            }).catch(function (error) {
                // Display a warning in case of an error
                self.displayWarning('An error occurred: ' + error.message);
            });
        },

        // Custom method to update options of a selection field
        updateSelectFieldOptions: function (selectField, options) {
            // Clear existing options
            selectField.empty();

            // Add new options based on the fetched data
            options.forEach(function (option) {
                selectField.append('<option value="' + option.id + '">' + option.name + '</option>');
            });
        },
    });
});