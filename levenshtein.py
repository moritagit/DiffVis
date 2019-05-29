# -*- coding: utf-8 -*-


import sys
import functools


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
    def build_cost_table(seq1, seq2):
        """Builds cost table.


        Args:
            seq1 (iterable): Source sequence.
            seq2 (iterable): Target sequence.

        Returns:
            cost_table (tuple[tuple[int]]): Cost table.
        """
        m, n = len(seq1), len(seq2)
        cost_table = Levenshtein.init_cost_table(m, n)
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost_insert = cost_table[i-1][j] + Levenshtein.EDIT2COST['insert']
                cost_delete =  cost_table[i][j-1] + Levenshtein.EDIT2COST['delete']
                cost = 0 if (seq1[i-1] == seq2[j-1]) else Levenshtein.EDIT2COST['replace']
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
    def build_edit_history(cost_table, i=0, j=0):
        """Builds edit history from cost table.

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
