from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Subsession


def vars_for_all_templates(self):
    return dict(
        page=self.subsession.round_number
    )


class Decision(Page):

    form_model = 'player'
    form_fields = ['choice']

    def vars_for_template(self):
        return dict(
            options=self.participant.vars['choice_sets'][self.round_number - 1],
            options_coded=self.participant.vars['options'][self.round_number - 1],
            options_index=self.participant.vars['options_index'][self.round_number - 1]
        )


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [Decision]
