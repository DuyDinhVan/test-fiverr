from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    total_possible_score = fields.Float("Total Possible Score", compute="_compute_scoring_values", store=True, compute_sudo=True)
    fraction_score = fields.Char("Score (/)", compute="_compute_scoring_values", store=True, compute_sudo=True)

    def _compute_scoring_values(self):
        for user_input in self:
            # sum(multi-choice question scores) + sum(simple answer_type scores)
            total_possible_score = 0
            for question in user_input.predefined_question_ids:
                if question.question_type == 'simple_choice':
                    total_possible_score += max([score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0], default=0)
                elif question.question_type == 'multiple_choice':
                    total_possible_score += sum(score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0)
                elif question.is_scored_question:
                    total_possible_score += question.answer_score

            user_input.total_possible_score = total_possible_score
            if total_possible_score == 0:
                user_input.scoring_percentage = 0
                user_input.scoring_total = 0
                user_input.fraction_score = 0
            else:
                score_total = sum(user_input.user_input_line_ids.mapped('answer_score'))
                user_input.scoring_total = score_total
                score_percentage = (score_total / total_possible_score) * 100
                user_input.fraction_score = f'{score_total}/{total_possible_score}'
                user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0
