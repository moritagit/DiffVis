# -*- coding: utf-8 -*-


"""diffvis.py

Visualize difference between two sequences by coloring.
Sequences must be iterable.
Not only string, but also list of words (tokenized sentence) can be used.
"""


from .edit_distance import Levenshtein, format_cost_table, format_edit_history
from .formatter import ConsoleFormatter, HTMLFormatter, HTMLTabFormatter


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='diffvis.py',
        usage='python edit_distance.py <source> <target> -p',
        description='Visualize difference between two strings',
        epilog='end',
        add_help=True,
        )
    parser.add_argument(
        'source',
        help='source string',
        action='store',
        )
    parser.add_argument(
        'target',
        help='target string',
        action='store',
        )
    parser.add_argument(
        '-p', '--padding',
        help='flag to pad',
        action='store_true',
        required=False,
        )

    args = parser.parse_args()
    source = args.source
    target = args.target
    padding = args.padding

    dv = DiffVis(source, target)
    dv.build()
    print(dv.generate_comparison(mode='console', padding=padding))


def make_diff2blank(source, target, edit_history, blank='<blank>'):
    """Converts unmatch parts between source and target to blank.

    Args:
        source (iterable): Source sequence.
        target (iterable): Target sequence.
        edit_history (tuple[str]): Edit history.
        blank (str): String for blank. Defaluts to '<blank>'.

    Returns:
        template (list[str]): Sequence that has common parts of source and target, and has blank in non-common parts.
    """
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
    """Visualizes difference between two sequences by coloring.

    Args:
        source (iterable): Source sequence.
        target (iterable): Target sequence.

    Attributes:
        cost_table (tuple[tuple[int]]): Cost table.
        edit_history (tuple): History of edition.
        __source (iterable): Source sequence.
        __target (iterable): Target sequence.
    """
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
        """Builds cost table and edit history."""
        self.cost_table = Levenshtein.build_cost_table(self.__source, self.__target)
        self.edit_history = Levenshtein.trace_back(self.cost_table)

    def distance(self, normalize=False):
        """Measures Lebenshtein distance between source and target.

        Args:
            normalize (bool):
            Determines whether to normalize Levenshtein distance,
            deviding by longer length of the input two sequences.
            Defaults to False.

        Returns:
            dist (float): Levenshtein distance.
        """
        dist = Levenshtein.measure(
            self.__source, self.__target,
            cost_table=self.cost_table,
            normalize=normalize,
            )
        return dist

    def edit_distance(self):
        """Calculates edit distance without cost.
        (The word 'edit distance' is not used corectly.)

        Returns:
            dist (float): Edit distance.
        """
        dist = len([operation for operation in self.edit_history if operation != 'match'])
        return dist

    def template(self, use_str=False, blank='<blank>'):
        """Make template from source and target
        by filling the difference with 'blank'.

        Args:
            use_str (bool): Determines whether to return str or list.
                Defaults to False.
            blank (str): String for blank. Defaluts to '<blank>'.

        Returns:
            template (list[str]): Sequence that has common parts of source and target, and has blank in non-common parts.
        """
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

    def visualize(self, mode='Console', padding=True):
        """Visualize the difference between source and target.
        This method only inputs formatter to generate_comparison method depending on the mode.
        So you can use generate_comparison method with your original formatter.
        Output mode can be chosen from:
            * Console: to be shown in console
            * HTML: HTML format
            * HTMLTab: HTML format (table)

        Notes:
            * Console output is not for Windows.

        Args:
            mode (str): Output mode.
                Must be hosen from 'Console', 'HTML', or HTMLTab'.
                Defaults to 'Console'
            padding (bool): Determines whether to pad or not.
                Defaults to True.

        Returns:
            output (str): Output.
        """
        mode = mode.lower()
        if mode in ['console']:
            formatter = ConsoleFormatter()
        elif mode in ['html']:
            formatter = HTMLFormatter()
        elif mode in ['htmltab']:
            formatter = HTMLTabFormatter()
        else:
            raise ValueError(f'Unknown mode: {mode}')
        output = self.generate_comparison(formatter, padding=padding)
        return output

    def generate_comparison(self, formatter, padding=True):
        """Visualize the difference between source and target,
        formatting by formatter.

        Args:
            formatter (formatter.Formatter): Formatter.
            padding (bool): Determines whether to pad or not.
                Defaults to True.

        Returns:
            output (str): Output.
        """
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

        output = formatter.concatenate(result_source, result_target)
        return output


if __name__ == '__main__':
    main()
