"""
LatexTable class (also tacked on ListTable temporarily)

This duplicates a LOT of functionality from `matrix2latex.py`.
Possible implementation (using doctest syntax):
>>> from matrix2latex import matrix2latex as m2ltx
>>> algnmt = '@{}rr@{ $\pm$ }lr@{ $\pm$ }lr@{}'
>>> hr = '''[[''] + 5 * [title],
...       [r'$\mu$ (-)'] + 2 * [r'$\eta_2$ (-)] + 2 * [r'$B_0$ ($\mu$G)']
...        + [r'$\chi^2$']]'''
>>> fmtcol = 'stuff'  # Here parse sigfigs, depending on error
>>> # note: fmtcol varies w/ row, not implemented in m2ltx
>>> m2ltx(data, headerRow = hr, formatColumn = fmtcol, alignment = algnmt)


I'd like to extend matrix2latex by adding support for data w/errors;
* use errors to compute # of sigfigs and supply that as an argument
* use \e in LaTeX to change exponential notation formatting, rather than
  manually editing floats

Aaron Tran
August 2014 (originally)
March 2016 - copied from Tycho project to G309.2-0.6 project
"""

#import numpy as np
import re

# ========================
# LatexTable and utilities
# ========================

def merge_latex_tables(tab1, tab2, indent=5):
    """Smush two tables together -- combine headers and rows
    The rowspecs (precisions) of each indiv. table are preserved in rspec
    BUT, number of rows MUST be consistent
    2nd table rows are pushed to a newline w/ indent, when joined
    """

    tab3 = LatexTable([], [], '')  # The empty vessel to be filled with life
    tab3.types = tab1.types + tab2.types  # list of types
    tab3.cspec = tab1.cspec + tab2.cspec  # str for \begin{tabular}{...}
    tab3.title_row = tab1.title_row + ' & ' + tab2.title_row  # str
    tab3.header_rows = []
    for h1, h2 in zip(tab1.header_rows, tab2.header_rows):
        tab3.header_rows.append(h1 + ' & ' + h2)  # str

    t1r = tab1.rows
    t2r = tab2.rows
    if len(t1r) < len(t2r):
        t1r = t1r + (len2-len1) * [tab1.rspec]
    elif len(t2r) < len(t1r):
        t2r = t2r + (len1-len2) * [tab2.rspec]
    rowsep = '\n' + ' '*indent + '& '
    tab3.rows = [rowsep.join([r1, r2]) for r1, r2 in zip(t1r, t2r)]  # str, row

    return tab3


class LatexTable(object):
    """Format numpy array data with errors in a nice LaTeX'd table.
    Designed for LaTeX package 'booktabs'

    For this class, some to-dos (low priority)
    2. allow concatenating tables together (horizontally)
    """
    def __init__(self, col_headers, types, title, prec=4):
        """
        Initialize empty LatexTable with title, column headers, and column
        "data-with-error" types.

        col_headers = list of header rows for each column
            this is a list of lists... so e.g. if you want just a single row
            column header, do: [['column a', 'column b', ...]]

            Each col_header row shall have the same number of elements as types

        Types = list of column "types". 0,1,2 = no/single/double +/- errors
        Should work fine on empty table, for manipulation...
        0: plain number, default {:0.[prec]g} formatting
        1: number w/ +/- error, uses +/- symbol as column separator to align
        2: number w/ distinct +/- errors, aligns to left
        str: any string format specifier you like (single right aligned column)

        'add_row' takes an arbitrary length list which should match the length
        of input "types" array: +2 for each "type 1" column, +1 for rest
        """
        self.prec = prec    # Save for user access
        self.types = types  # Need for e.g., self.ncols()

        # Build column specification
        cspec = []
        for t in types:
            if t == 1:  # number with +/- error
                cspec.append(r'r@{ $\pm$ }l')  # Align to column sep
            elif t == 2:  # number with super/sub script error
                cspec.append('l')  # Align output to values, not errors
            else:
                cspec.append('r')
        self.cspec = ''.join(cspec)

        # Build title row spanning all column
        if self.ncols() > 1:
            self.title_row = r'\multicolumn{'+str(self.ncols())+'}{c}{'+title+r'}'
        elif self.ncols() == 1:
            self.title_row = title
        else:
            self.title_row = r''

        # Build list of column header rows
        self.header_rows = []
        for header_row in col_headers:
            hrow_list = []
            for t, label in zip(types, header_row):
                if t == 1:
                    hrow_list.append(r'\multicolumn{2}{c}{' + str(label) + r'}')
                else:
                    hrow_list.append(label)
            self.header_rows.append(' & '.join(hrow_list))
        # TODO outstanding discrepancy. User-facing arg name is "col_headers"
        # to help clarify meaning.
        # But internal naming is header_rows to be more concise.
        # Some ambiguity w/ use of "header" to refer to entire table header,
        # instead of column headers alone.

        # Build row spec (string)
        rlist = []
        fmt = '{:0.' + str(self.prec) + 'f}'  # Forces decimal pt notation
        for t in types:
            if t == 0:  # General number
                rlist.append('{:0.' + str(self.prec) + 'g}')
            elif t == 1:  # Single error splits into two columns
                rlist.extend(2*['$'+fmt+'$'])
            elif t == 2:  # Double error w/ braces around all values
                rlist.append('${{'+fmt+'}}^{{+'+fmt+'}}_{{-'+fmt+'}}$')
            else:
                rlist.append(t)  # Supply your own spec
        self.rspec = ' & '.join(rlist)

        # Initialize rows to be filled with rspec-formatted strings
        self.rows = []

    def ncols(self):
        """Compute number of LaTeX/internal columns from self.types"""
        return sum([2 if t == 1 else 1 for t in self.types])

    def add_row(self, *args):
        """Add row to table (self.rows), applying self.rspec format
        If giving two errors, positive err comes first
        """
        self.rows.append(self.rspec.format(*args))

    # -----------------------------------
    # Self-assembly / prettyprint methods
    # -----------------------------------

    def get_header(self):
        """List of strings, one per table row. cspec, title_row, column headers.
        Doesn't deal with nuances of where to cut multicolumns/lines
        """
        h_list = [r'\begin{tabular}{@{}' + self.cspec + '@{}}']
        h_list.append(r'\toprule')
        h_list.append(self.title_row + r' \\')
        h_list.append(r'\midrule')
        for hrow in self.header_rows:
            h_list.append(hrow + r' \\')
        h_list.append(r'\midrule')

        return h_list

    def get_rows(self):
        """List of row strings with latex line breaks attached"""
        return map(lambda x: x + r' \\', self.rows)

    def get_footer(self):
        """List of footer rows with latex line breaks attached"""
        return [r'\bottomrule', r'\end{tabular}']

    def get_table(self):
        return self.get_header() + self.get_rows() + self.get_footer()

    def __str__(self):
        return '\n'.join(self.get_table())


# =========================
# Table for IPython display
# =========================

class ListTable(list):
    """ Overridden list class which takes a 2-dimensional list of
    the form [[1,2,3],[4,5,6]], and renders an HTML Table in ipynb.
    Source: http://calebmadrigal.com/display-list-as-table-in-ipython-notebook/
    """

    def _repr_html_(self):
        html = ["<table style='font-family: monospace; font-size: 10pt'>"]
        for row in self:
            html.append("<tr>")

            for col in row:
                html.append("<td>{0}</td>".format(col))

            html.append("</tr>")
        html.append("</table>")
        return ''.join(html)


if __name__ == '__main__':
    pass
