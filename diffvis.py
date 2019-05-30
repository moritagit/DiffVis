# -*- coding: utf-8 -*-


from .edit_distance import Levenshtein, format_cost_table, format_edit_history
from .formatter import ConsoleFormatter, HTMLFormatter, HTMLTabFormatter


def make_diff2blank(source, target, edit_history, blank='<blank>'):
    template = []
    i, j = 0, 0
    for operation in edit_history:
        if operation == 'match':
            template.append(source[i])
            i += 1
            j += 1
        elif operation == 'replace':
            template.append(blank)
            i += 1
            j += 1
        elif operation == 'delete':
            template.append(blank)
            i += 1
        elif operation == 'insert':
            template.append(blank)
            j += 1

    if not template:
        return template

    # delete duplicates of <blank>
    template_new = [template[0]]
    for i in range(1, len(template)):
        elem_now = template[i]
        elem_last = template[i-1]
        if (elem_now == blank) and (elem_last == blank):
            continue
        else:
            template_new.append(elem_now)
    template = template_new

    # if only blank, return empty string
    if template == [blank]:
        template = ['']
    return template


class DiffVis(object):
    COLOR_SETTINGS = {
        'base': 'green',
        'source': 'red',
        'target': 'blue',
        }
    def __init__(self, source, target):
        self.__source = source
        self.__target = target
        self.cost_table = None
        self.edit_history = None

    def build(self):
        self.cost_table = Levenshtein.build_cost_table(self.__source, self.__target)
        self.edit_history = Levenshtein.trace_back(self.cost_table)

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

    def template(self, use_str=False, blank='<blank>'):
        tmp = make_diff2blank(
            self.__source,
            self.__target,
            self.edit_history,
            blank=blank,
            )
        if use_str:
            tmp = ''.join(tmp)
        return tmp

    def format_cost_table(self):
        return format_cost_table(self.__source, self.__target, self.cost_table)

    def format_edit_history(self):
        return format_edit_history(self.edit_history)

    def generate_comparison(self, mode='console', padding=True):
        mode = mode.lower()
        if mode in ['console']:
            formatter = ConsoleFormatter()
        elif mode in ['html']:
            formatter = HTMLFormatter()
        elif mode in ['htmltab']:
            formatter = HTMLTabFormatter()
        else:
            raise ValueError(f'Unknown mode: {mode}')
        result = self._generate_comparison(formatter, padding=padding)
        return result

    def _generate_comparison(self, formatter, padding=True):
        source = self.__source
        target = self.__target
        color_base = DiffVis.COLOR_SETTINGS['base']
        color_source = DiffVis.COLOR_SETTINGS['source']
        color_target = DiffVis.COLOR_SETTINGS['target']

        def _form(text, color, length):
            text = formatter.escape(text)
            if padding:
                text = formatter.pad(text, length)
            text = formatter.colorize(text, color)
            text = formatter.form(text)
            return text

        i = 0
        j = 0
        result_source = ''
        result_target = ''
        for operation in self.edit_history:
            if operation == 'match':
                length = max(len(source[i]), len(target[j]))
                result_source += _form(source[i], color_base, length)
                result_target += _form(target[j], color_base, length)
                i += 1
                j += 1
            elif operation == 'replace':
                length = max(len(source[i]), len(target[j]))
                result_source += _form(source[i], color_source, length)
                result_target += _form(target[j], color_target, length)
                i += 1
                j += 1
            elif operation == 'delete':
                length = len(source[i])
                result_source += _form(source[i], color_source, length)
                result_target += _form('', color_base, length)
                i += 1
            elif operation == 'insert':
                length = len(target[j])
                result_source += _form('', color_base, length)
                result_target += _form(target[j], color_target, length)
                j += 1

        result = formatter.concatenate(result_source, result_target)
        return result
