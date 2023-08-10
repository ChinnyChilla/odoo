/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
const { Component } = owl;

export class Suggestion extends Component {
	/**
	 * @returns {SuggestionView}
	 */
	get suggestionView() {
		return this.props.record;
	}

}

Object.assign(Suggestion, {
	props: { record: Object },
	template: 'suggest.Suggestion',
});

registerMessagingComponent(Suggestion);

