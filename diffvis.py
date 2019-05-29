# -*- coding: utf-8 -*-


from .levenshtein import Levenshtein
from .formatter import ConsoleFormatter, HTMLFormatter, HTMLTabFormatter


class DiffVis(object):
    COLOR_SETTINGS = {
        'base': 'green',
        'correct': 'blue',
        'wrong': 'red',
        }
    def __init__(self, source, target):
        self.__source = source
        self.__target = target
        self.cost_table = None
        self.edit_history = None

    def build(self):
        self.cost_table = Levenshtein.build_cost_table(self.__source, self.__target)
        self.edit_history = Levenshtein.build_edit_history(self.cost_table)

    def distance(self, normalize=False):
        dist = Levenshtein.measure(
            self.__source, self.__target,
            cost_table=self.cost_table,
            normalize=normalize,
            )
        return dist

    def edit_distance(self):
        dist = len([operation for operation in self.edit_history if operation != 'match'])
        return dist

    def generate_comparison(self, mode='console'):
        mode = mode.lower()
        if mode in ['console']:
            formatter = ConsoleFormatter()
        elif mode in ['html']:
            formatter = HTMLFormatter()
        elif mode in ['htmltab']:
            formatter = HTMLTabFormatter()
        else:
            raise ValueError(f'Unknown mode: {mode}')
        result = self._generate_comparison(formatter)
        return result

    def _generate_comparison(self, formatter):
        seq1 = self.__source
        seq2 = self.__target

        def _form(text, color):
            text = formatter.escape(text)
            text = formatter.pad(text)
            text = formatter.colorize(text, color)
            text = formatter.form(text)
            return text

        i = 0
        j = 0
        result_source = ''
        result_target = ''
        for operation in self.edit_history:
            if operation == 'match':
                result_source += _form(seq1[i], DiffVis.COLOR_SETTINGS['base'])
                result_target += _form(seq2[j], DiffVis.COLOR_SETTINGS['base'])
                i += 1
                j += 1
            elif operation == 'replace':
                result_source += _form(seq1[i], DiffVis.COLOR_SETTINGS['wrong'])
                result_target += _form(seq2[j], DiffVis.COLOR_SETTINGS['correct'])
                i += 1
                j += 1
            elif operation == 'delete':
                result_source += _form(seq1[i], DiffVis.COLOR_SETTINGS['wrong'])
                result_target += _form(' ', DiffVis.COLOR_SETTINGS['base'])
                i += 1
            elif operation == 'insert':
                result_source += _form(' ', DiffVis.COLOR_SETTINGS['base'])
                result_target += _form(seq2[j], DiffVis.COLOR_SETTINGS['correct'])
                j += 1

        result = formatter.output(result_source, result_target)
        return result
