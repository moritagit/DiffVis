# -*- coding: utf-8 -*-


"""diffvis.py

Visualize difference between two sequences by coloring.
Sequences must be iterable.
Not only string, but also list of words (tokenized sentence) can be used.
"""


from .string_distance import Levenshtein, LongestCommonSubsequence
from .string_distance import format_cost_table, format_edit_history, extract_common_parts
from .formatter import ConsoleFormatter, HTMLFormatter, HTMLTabFormatter


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='diffvis.py',
        usage='python diffvis.py <source> <target> -p',
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
    parser.add_argument(
        '-m', '--mode',
        help='sequence alignment algorythm. Levenshtein or LCS can be used.',
        action='store',
        required=False,
        default='Levenshtein',
        )

    args = parser.parse_args()
    source = args.source
    target = args.target
    padding = args.padding
    mode = args.mode

    dv = DiffVis(source, target, alignment=mode)
    dv.build()
    print(dv.visualize(mode='console', padding=padding))


class DiffVis(object):
    """Visualizes difference between two sequences by coloring.

    Args:
        source (iterable): Source sequence.
        target (iterable): Target sequence.
        alignment (str): Sequence alignment model name.
            Levenshtein or LCS can be chosen now.
            Defaults to Levenshtein.

    Attributes:
        source (iterable): Source sequence.
        target (iterable): Target sequence.
        cost_table (tuple[tuple[int]]): Cost table.
        edit_history (tuple): History of edition.
    """
    COLOR_SETTINGS = {
        'base': 'green',
        'source': 'red',
        'target': 'blue',
        }
    def __init__(self, source, target, alignment='Levenshtein'):
        self.source = source
        self.target = target
        self.cost_table = None
        self.edit_history = None
        self.template = None

        if alignment in ['Levenshtein', 'EditDistance']:
            self.Model = Levenshtein
        elif alignment in ['LongestCommonSubsequence', 'LCS']:
            self.Model = LongestCommonSubsequence
        else:
            raise ValueError(f'Unknown alignment mode: {alignment}')

    def build(self):
        """Builds cost table and edit history."""
        model = self.Model(self.source, self.target)
        model.build()
        self.cost_table = model.cost_table
        self.edit_history = model.edit_history

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
        dist = self.Model.measure(
            self.source, self.target,
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

    def make_template(self, return_str=False, blank='<blank>'):
        """Make template from source and target
        by filling the difference with 'blank'.

        Args:
            return_str (bool): Determines whether to return str or list.
                Defaults to False.
            blank (str): String for blank. Defaluts to '<blank>'.

        Returns:
            template (list[str]): Sequence that has common parts of source and target, and has blank in non-common parts.
        """
        template = extract_common_parts(
            self.source,
            self.target,
            self.edit_history,
            blank=blank,
            )
        self.template = template
        if return_str:
            template = ''.join(template)
        return template

    def format_cost_table(self):
        return format_cost_table(self.source, self.target, self.cost_table)

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
        source = self.source
        target = self.target
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
