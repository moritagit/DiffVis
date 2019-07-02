# -*- coding: utf-8 -*-


"""string_similarity.py

Calculates similarity between two strings.
And sequence alignment is implemented as a by-product.

Similarity:
    * Edit distance (Levenshtein distance)
    * Least Common Subsequence (LCS)
"""


import sys
import functools


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='string_similarity.py',
        usage='python string_similarity.py <source> <target> -n -a',
        description='Calculates similarity between two strings',
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
        '-n', '--normalize',
        help='flag to normalize similarity',
        action='store_true',
        required=False,
        )
    parser.add_argument(
        '-a', '--all',
        help='flag to output all the results',
        action='store_true',
        required=False,
        )

    args = parser.parse_args()
    source = args.source
    target = args.target
    normalize = args.normalize
    output_all = args.all

    if not output_all:
        distance = Levenshtein.measure(source, target, normalize=normalize)
        print(distance)
    else:
        cost_table = Levenshtein.build_cost_table(source, target)
        edit_history = Levenshtein.trace_back(cost_table)
        dist = Levenshtein.measure(source, target, cost_table, normalize=False)
        dist_norm = Levenshtein.measure(source, target, cost_table, normalize=True)
        print(f'Levenshtein Distance: {dist}')
        print(f'Normalized Levenshtein Distance: {dist_norm:.3f}')
        print()
        print(format_cost_table(source, target, cost_table))
        print()
        print(format_edit_history(edit_history))
    return


def format_cost_table(source, target, cost_table):
    """Formats cost table.

    Args:
        source (string): Source string.
        target (string): Target string.
        cost_table (tuple[tuple[int]]): Padded cost table.

    Returns:
        result (str): Formatted cost table.
    """
    # error handling
    __max_len_source_elem = max([len(elem) for elem in source])
    __max_len_target_elem = max([len(elem) for elem in target])
    if max(__max_len_source_elem, __max_len_target_elem) < 1:
        raise ValueError('Elements of source and target sequences must be 1 or 0.')

    # settings
    m, n = len(source), len(target)
    column_width = max(max([len(str(elem)) for elem in row]) for row in cost_table)
    column_width += 2
    cell_form = '{:>' + str(column_width) + '}'
    line = '\n' + '-' * ((column_width+1) * (n+2) + 1) + '\n'

    # generate
    result = 'Cost Table'

    # add target string
    result += line
    result += '|' + cell_form.format('') + '|'
    result += cell_form.format('') + '|'
    for j in range(n):
        result += cell_form.format(target[j]) + '|'
    result += line

    # add source string and cost table
    result += '|' + cell_form.format('') + '|'
    for j in range(n+1):
        value = cost_table[0][j]
        result += cell_form.format(value) + '|'
    result += line

    for i in range(1, m+1):
        result += '|' + cell_form.format(source[i-1]) + '|'
        for j in range(n+1):
            value = cost_table[i][j]
            result += cell_form.format(value) + '|'
        result += line
    result = result[:-1]  # delete last \n
    return result


def format_edit_history(edit_history):
    """Formats edit history.

    Args:
        edit_history (tuple[str]): Edit history.

    Returns:
        result (str): Formatted edit history.
    """
    result = 'Edit History\n\t'
    result += '\n\t'.join(edit_history)
    return result


class Levenshtein(object):
    """Calculates Levenshtein distance
    and makes edit history from cost table.

    Attributes:
        EDIT2COST (dict): Mapping from edit operation to its cost.
    """
    EDIT2COST = {
        'match': 0,
        'insert': 1,
        'delete': 1,
        'replace': 1,
        }
    @staticmethod
    def measure(seq1, seq2, cost_table=None, normalize=False,):
        """Measures Lebenshtein distance between two input sequences.

        Args:
            seq1 (iterable): Source sequence.
            seq2 (iterable): Target sequence.
            cost_table (tuple[tuple]): Cost table.
                If is None, newly built.
                Defaults to None.
            normalize (bool):
                Determines whether to normalize Levenshtein distance,
                deviding by longer length of the input two sequences.
                Defaults to False.

        Returns:
            distance (float): Levenshtein distance.
        """
        m, n = len(seq1), len(seq2)
        len_max = max(m, n)
        if len_max == 0:
            return 0
        if not cost_table:
            cost_table = Levenshtein.build_cost_table(seq1, seq2)
        distance = cost_table[m][n]
        if normalize:
            distance /= len_max
        return distance

    @staticmethod
    def init_cost_table(m, n):
        """Initializes cost table (((m+1) x (n+1)) matrix).

        Args:
            m (int): Length of source sequence.
            n (int): Length of target sequence.

        Returns:
            cost_table (list[list]): Cost table.
        """
        cost_table = [[0] * (n+1) for _ in range(m+1)]

        for i in range(m+1):
            cost_table[i][0] = i * Levenshtein.EDIT2COST['insert']

        for j in range(n+1):
            cost_table[0][j] = j * Levenshtein.EDIT2COST['delete']

        return cost_table

    @staticmethod
    def build_cost_table(source, target):
        """Builds cost table.

        Args:
            source (iterable): Source sequence.
            target (iterable): Target sequence.

        Returns:
            cost_table (tuple[tuple[int]]): Cost table.
        """
        m, n = len(source), len(target)
        cost_table = Levenshtein.init_cost_table(m, n)
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost_insert = cost_table[i-1][j] + Levenshtein.EDIT2COST['insert']
                cost_delete =  cost_table[i][j-1] + Levenshtein.EDIT2COST['delete']
                cost = 0 if (source[i-1] == target[j-1]) else Levenshtein.EDIT2COST['replace']
                cost_replace = cost_table[i-1][j-1] + cost
                cost_table[i][j] = min(cost_insert, cost_delete, cost_replace)
        cost_table = tuple([tuple(row) for row in cost_table])
        return cost_table

    @staticmethod
    def pad_cost_table(cost_table):
        """Pads cost table with sys.maxsize
        to make stopper for search_edit_path.

        Args:
            cost_table (tuple[tuple[int]]): Cost table.

        Returns:
            cost_table (tuple[tuple[int]]): Padded cost table.
        """
        padded_table = []
        for k in range(len(cost_table)):
            padded_table.append(list(cost_table[k]) + [sys.maxsize])
        padded_table.append([sys.maxsize]*len(cost_table[0]))
        cost_table = tuple([tuple(row) for row in padded_table])
        return cost_table

    @staticmethod
    def trace_back(cost_table, i=0, j=0):
        """Traces back cost table and make edit history.

        Args:
            cost_table (tuple[tuple[int]]): Cost table.
            i (int): Row index of cost table.
            j (int): Column index of cost table.

        Returns:
            edit_history (tuple): History of edition.
        """
        cost_table = Levenshtein.pad_cost_table(cost_table)
        m = len(cost_table) - 1
        n = len(cost_table[0]) - 1
        edit_history = Levenshtein.search_edit_path(cost_table, m, n, i, j)
        if edit_history:
            edit_history = tuple(edit_history)
        return edit_history

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def search_edit_path(cost_table, m, n, i=0, j=0):
        """Searchs lowest cost path of edition.
        This method is called recursively,
        so is speeded up by memoization.

        Args:
            cost_table (tuple[tuple[int]]): Cost table.
            m (int): Length of source sequence.
            n (int): Length of target sequence.
            i (int): Row index of cost table.
            j (int): Column index of cost table.

        Returns:
            edit_history (list): History of edition.
        """
        # reach end of the strings
        if (i+1 == m) and (j+1 == n):
            return []

        # get cost
        cost_current = cost_table[i][j]
        cost_insert = cost_table[i][j+1]
        cost_delete = cost_table[i+1][j]
        cost_replace = cost_table[i+1][j+1]

        # check path
        has_passed_wrong_path = (
            (cost_insert < cost_current)
            or (cost_delete < cost_current)
            or (cost_replace < cost_current)
            )
        if has_passed_wrong_path:
            message = 'has passed wrong path:  '
            message += 'i = {}, j = {}, cur: {}, ins: {}, del: {}, rep: {}'.format(
                i, j, cost_current, cost_insert, cost_delete, cost_replace
                )
            #print(message)
            return None

        # check not out of table
        #if (i+1 < m) and (j+1 < n):
        if cost_replace != sys.maxsize:
            ret = Levenshtein.search_edit_path(cost_table, m, n, i+1, j+1)
            if ret != None:
                if cost_replace == cost_current:
                    return ['match'] + ret
                else:
                    return ['replace'] + ret

        # check not out of table and invalid pass
        #if (i+1 < m) and (cost_delete > cost_current):
        if (cost_delete != sys.maxsize) and (cost_delete > cost_current):
            ret = Levenshtein.search_edit_path(cost_table, m, n, i+1, j)
            if ret != None:
                return ['delete'] + ret

        # check not out of table and invalid pass
        #if (j+1 < n) and (cost_insert > cost_current):
        if (cost_insert != sys.maxsize) and (cost_insert > cost_current):
            ret = Levenshtein.search_edit_path(cost_table, m, n, i, j+1)
            if ret != None:
                return ['insert'] + ret


if __name__ == '__main__':
    main()
