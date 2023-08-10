from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_mail_thread_data(self, request_list):
        res = {'hasWriteAccess': False, 'hasReadAccess': True}
        if not self:
            res['hasReadAccess'] = False
            return res
        res['canPostOnReadonly'] = self._mail_post_access == 'read'

        self.ensure_one()
        try:
            self.check_access_rights("write")
            self.check_access_rule("write")
            res['hasWriteAccess'] = True
        except AccessError:
            pass
        if 'activities' in request_list:
            res['activities'] = self.activity_ids.activity_format()
        if 'attachments' in request_list:
            res['attachments'] = self._get_mail_thread_data_attachments()._attachment_format()
            res['mainAttachment'] = {'id': self.message_main_attachment_id.id} if self.message_main_attachment_id else [('clear',)]
        if 'followers' in request_list:
            res['followers'] = [{
                'id': follower.id,
                'partner_id': follower.partner_id.id,
                'name': follower.name,
                'display_name': follower.display_name,
                'email': follower.email,
                'is_active': follower.is_active,
                'partner': follower.partner_id.mail_partner_format()[follower.partner_id],
            } for follower in self.message_follower_ids]
        if 'suggestedRecipients' in request_list:
            res['suggestedRecipients'] = self._message_get_suggested_recipients()[self.id]
        if 'suggestions' in request_list:
            if 'suggestion_ids' not in self._fields:
                res['suggestions'] = []
            else:
                res['suggestions'] = self.suggestion_ids.format_suggestions()
        return res
    
    