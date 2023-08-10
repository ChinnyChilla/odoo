/** @odoo-module **/


import { registerPatch } from '@mail/model/model_core';
import { attr, many } from '@mail/model/model_field';
import { clear, insert} from '@mail/model/model_field_command';
import * as mailUtils from '@mail/js/utils';
const getSuggestedRecipientInfoNextTemporaryId = (function () {
	let tmpId = 0;
	return () => {
		tmpId += 1;
		return tmpId;
	};
})();

registerPatch({
	name: 'Thread',
	recordMethods: {
		async fetchData(requestList) {
			if (this.isTemporary) {
				return;
			}
			const requestSet = new Set(requestList);
			if (!this.hasActivities) {
				requestSet.delete('activities');
			}
			if (requestSet.has('attachments')) {
				this.update({ isLoadingAttachments: true });
			}
			if (!this.hasSuggestions) {
				requestSet.delete('suggestions')
			}
			if (requestSet.has('messages')) {
				this.cache.loadNewMessages();
			}
			const {
				activities: activitiesData,
				suggestions: suggestionsData,
				attachments: attachmentsData,
				canPostOnReadonly,
				followers: followersData,
				hasWriteAccess,
				mainAttachment,
				hasReadAccess,
				suggestedRecipients: suggestedRecipientsData,
			} = await this.messaging.rpc({
				route: '/mail/thread/data',
				params: {
					request_list: [...requestSet],
					thread_id: this.id,
					thread_model: this.model,
				},
			}, { shadow: true });
			if (!this.exists()) {
				return;
			}
			const values = { canPostOnReadonly, hasWriteAccess, mainAttachment, hasReadAccess };
			if (activitiesData) {
				Object.assign(values, {
					activities: activitiesData.map(activityData =>
						this.messaging.models['Activity'].convertData(activityData)
					),
				});
			}
			if (attachmentsData) {
				Object.assign(values, {
					areAttachmentsLoaded: true,
					isLoadingAttachments: false,
					originThreadAttachments: attachmentsData,
				});
			}
			if (followersData) {
				Object.assign(values, {
					followers: followersData.map(followerData =>
						this.messaging.models['Follower'].convertData(followerData)
					),
				});
			}
			if (suggestionsData) {
				Object.assign(values, {
					suggestions: suggestionsData.map(suggestionData =>
						this.messaging.models['Suggestion'].convertData(suggestionData)
					),
				});
			}
			if (suggestedRecipientsData) {
				const recipientInfoList = suggestedRecipientsData.map(recipientInfoData => {
					const [partner_id, emailInfo, lang, reason] = recipientInfoData;
					const [name, email] = emailInfo && mailUtils.parseEmail(emailInfo);
					return {
						email,
						id: getSuggestedRecipientInfoNextTemporaryId(),
						name,
						lang,
						partner: partner_id ? insert({ id: partner_id }) : clear(),
						reason,
					};
				});
				Object.assign(values, {
					suggestedRecipientInfoList: recipientInfoList,
				});
			}
			this.update(values);
			this.messaging.messagingBus.trigger('o-thread-loaded-data', { thread: this });
		},
	},
	fields: {
		suggestions: many('Suggestion', {
			inverse:'thread',
		}),
		hasSuggestions: attr({
			default: true,
		})
	}
})

