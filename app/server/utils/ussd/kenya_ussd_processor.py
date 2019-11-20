from typing import Optional
from functools import reduce

from server.models.ussd import UssdMenu, UssdSession
from server.models.user import User
from server.utils.phone import proccess_phone_number
from server.utils.ussd.kenya_ussd_state_machine import KenyaUssdStateMachine
from server import db


class KenyaUssdProcessor:
    @staticmethod
    def process_request(session_id: str, user_input: str, user: User) -> UssdMenu:
        session: Optional[UssdSession] = UssdSession.query.filter_by(session_id=session_id).first()
        # returning session
        if session:
            if user_input == "":
                return UssdMenu.find_by_name('exit_invalid_input')
            elif user_input.split('*')[-1] == 0:
                return UssdMenu.find_by_name(session.state).parent()
            else:
                new_state = KenyaUssdProcessor.next_state(session, user_input, user)
                return UssdMenu.find_by_name(new_state)
        # new session
        else:
            if user.is_resetting():
                if user.pin_failed_attempts() >= 3:
                    return UssdMenu.find_by_name('exit_pin_blocked')
                elif user.preferred_language is None:
                    return UssdMenu.find_by_name('initial_language_selection')
                else:
                    return UssdMenu.find_by_name('initial_pin_entry')
            else:
                return UssdMenu.find_by_name('start')
            
    @staticmethod
    def next_state(session: UssdSession, user_input: str, user) -> UssdMenu:
        state_machine = KenyaUssdStateMachine(session, user)
        state_machine.feed_char(user_input.split('*')[-1])
        new_state = state_machine.state

        session.state = new_state
        # db.session.commit()
        return new_state

    @staticmethod
    def replace_vars(menu: UssdMenu, ussd_session: UssdSession, display_text: str, user: User) -> str:
        replacements = [['%support_phone%', '+254757628885']]

        if menu.name == 'about_my_business':
            replacements.append(['%user_bio%', user.bio])
        elif menu.name == 'send_token_confirmation':
            phone = proccess_phone_number(ussd_session.session_data['recipient_phone'], 'KE')
            recipient = User.query.filter_by(phone=phone).first()
            replacements.append(['%recipient_phone%', recipient.user_details()])
            # TODO(ussd): this is not a thing yet!!
            token = ussd_session.user.community_token
            replacements.append(['%token_name%', token.name])
            replacements.append(['%transaction_amount%', ussd_session.session_data['transaction_amount']])
            replacements.append(['%transaction_reason%', ussd_session.session_data['transaction_reason']])
        elif menu.name == 'exchange_token_confirmation':
            phone = proccess_phone_number(ussd_session.session_data['agent_phone'], 'KE')
            agent = User.query.filter_by(phone=phone).first()
            replacements.append(['%agent_phone%', agent.user_details])
            # TODO(ussd): this is not a thing yet!!
            token = ussd_session.user.community_token
            replacements.append(['%token_name%', token.name])
            replacements.append(['%exchange_amount%', ussd_session.session_data['exchange_amount']])
        elif 'pin_authorization' in menu.name or 'current_pin' in menu.name:
            if user.pin_failed_attempts() > 0:
                # TODO(ussd): replace this with i18n placeholders
                if user.preferred_language == 'sw_KE':
                    # TODO(ussd): pin_failed_attempts isn't a thing yet!
                    replacements.append(['%remaining_attempts%', "Una majaribio {} yaliyobaki.".format(3 - user.pin_failed_attempts)])
                else:
                    replacements.append(['%remaining_attempts%', "You have {} attempts remaining.".format(3 - user.pin_failed_attempts)])
            else:
                replacements.append(['%remaining_attempts%', ''])
        elif menu.name == 'directory_listing' or menu.name =='send_token_reason':
            usages = user.get_most_relevant_transfer_usage()
            menu_options = ''
            for i, usage in enumerate(usages):
                business_usage_string = None
                if usage.translations is not None and user.preferred_language is not None:
                    business_usage_string = usage.translations.get(
                        user.preferred_language)
                if business_usage_string is None:
                    business_usage_string = usage.name
                message_option = '\n%d. %s' % (i+1, business_usage_string)
                menu_options += message_option
            replacements.append(['%options%', menu_options])
        return reduce(lambda text, r: text.replace(r[0], r[1]), replacements, display_text)
