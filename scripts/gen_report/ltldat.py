#!/usr/bin/env python2.7

"Module for little data processing"

import math

class ATable:
    title = None    # string
    legend = None   # list of strings
    rows = None     # list of dicts[column name: value]

    def __init__(self, title, legend, rows):
        """received `rows` is list of list."""
        self.title = title
        self.legend = legend
        self.rows = []
        for row in rows:
            self.rows.append({legend[i]: row[i] for i in range(len(legend))})

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        str_ = "title: %s\n" % self.title
        str_ += "%s" % self.legend + "\n"
        for row in self.rows:
            str_ += "%s\n" % [row[cname] for cname in self.legend]
        return str_

    def item_at(self, row, col):
        return self.rows[row][col]

    def update_at(self, row, col, val):
        self.rows[row][col] = val

    def nr_rows(self):
        return len(self.rows)

    def remove_row(self, idx):
        del self.rows[idx]

    def replace_legend(self, oldlegend, newlegend):
        for idx, name in enumerate(self.legend):
            if name == oldlegend:
                self.legend[idx] = newlegend
        for row in self.rows:
            row[newlegend] = row.pop(oldlegend)
        return self

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_legend(self):
        return self.legend

    def append_column(self, col_name, generator):
        self.legend.append(col_name)
        for idx in range(len(self.rows)):
            self.rows[idx][col_name] = generator(idx)
        return self

    def convert_column(self, col_name, converter):
        for idx in range(len(self.rows)):
            self.rows[idx][col_name] = converter(idx)
        return self

    def csv(self):
        lines = []
        lines.append("title, %s" % self.title)
        lines.append(", ".join(str(x) for x in self.legend))
        for row in self.rows:
            lines.append(", ".join(
                [str(row[cname]) for cname in self.legend]))
        return '\n'.join(lines)

    def human_readable_txt(self):
        txt = "# %s\n" % self.title
        txt += "\t".join(self.legend) + "\n"
        for row in self.rows:
            txt += "\t".join(
                [str(row[cname]) for cname in self.legend]) + "\n"
        return txt.strip()

    def normalize(self, basis_idx=1, exclude_cols=[0]):
        rows = []
        for row in self.rows:
            rows.append([row[cname] for cname in self.legend])
        basevals = [r[basis_idx] for r in rows]

        for ri, row in enumerate(rows):
            for idx, field in enumerate(row):
                if idx in exclude_cols:
                    continue
                v = field
                try:
                    v = float(v) / float(basevals[ri])
                except ValueError:
                    pass
                except ZeroDivisionError:
                    v = -0.1
                row[idx] = v
        return ATable(self.title, self.legend, rows)

def wrong_csv_format_check(csv):
    lines = [l.strip() for l in csv.split('\n')]
    fields = [f.strip() for f in lines[0].split(',')]
    if len(fields) != 2:
        print "title line has %d (>2) fields" % len(fields)
        return True
    if fields[0] != "title":
        print "title line should have keyword 'title' but '%s'" % fields[0]
        return True

    nr_legends = len(lines[1].split(','))
    for idx, l in enumerate(lines[2:]):
        nr_fields = len(l.split(','))
        if nr_fields != nr_legends:
            print "line %d has %d fields but # of legends are %d" % (
                    2 + idx, nr_fields, nr_legends)
            print "the line: `%s`" % l
            return True
    return False

def wrong_human_readable_txt(text):
    text = text.strip()
    records = text.split('\n\n\n')

    nr_rows = len(records[1].split('\n'))
    xvalues = []

    for ridx, rec in enumerate(records[1:]):
        ridx += 1
        nr_lines = len(rec.split('\n'))
        if nr_lines == 0:
            print "record %d has no data at all" % ridx
            return True

        if nr_lines != nr_rows:
            print "record %d has %d rows but first record has %d rows" % (
                    ridx, nr_lines, nr_rows)
            return True

        compare_xvalues = []
        for l in rec.split('\n')[1:]:
            if len(l.split()) < 2:
                print "each line should have at least two fields"
                return True
            if ridx == 1:
                xvalues.append(l.split()[0].strip())
            else:
                compare_xvalues.append(l.split()[0].strip())
        if ridx > 1 and xvalues != compare_xvalues:
            print "xvalues of record %d is '%s' but record 0 has '%s'" % (
                    ridx, ' '.join(compare_xvalues), ' '.join(xvalues))
            return True
    return False

def from_csv(csv):
    """Parse csv text and construct a table."""
    if wrong_csv_format_check(str(csv).strip()):
        return False

    lines = csv.split('\n')
    title = lines[0].split(',')[1].strip()
    legend = [x.strip() for x in lines[1].split(',')]
    rows = []
    for line in lines[2:]:
        rows.append([x.strip() for x in line.split(',')])
    return ATable(title, legend, rows)

def from_human_readable_records(text):
    """Parse line-base data and construct a table."""
    text = text.strip()
    if wrong_human_readable_txt(text):
        return False
    records = text.split('\n\n\n')
    title = records[0].strip()
    legend = []
    rows = []
    for ridx, rec in enumerate(records):
        lines = [x.strip() for x in rec.split('\n')]
        if ridx == 0:
            legend.append("xv")
        else:
            legend.append(lines[0])
        for idx, l in enumerate(lines[1:]):
            if ridx == 1:
                rows.append([])
                rows[idx].append(l.split()[0])
            rows[idx].append(l.split()[1])
    return ATable(title, legend, rows)

def pick_fields(table, fields):
    """Reconstruct table with selected fields only"""
    new_rows = []
    for row in table.rows:
        new_rows.append([row[col] for col in fields])
    return ATable(table.title, fields, new_rows)

def exclude_fields(table, exclude_fields):
    """Copy table with selected fields only"""
    legend = []
    for colname in table.legend:
        if colname in exclude_fields:
            continue
        legend.append(colname)
    return pick_fields(table, legend)

def merge(tables):
    """Merge multiple tables into one tables.

    Tables should have same legend and same number of rows.  If tables have
    different number of rows, compensate() function may be helpful.
    Each name of tables should be unique.
    """
    new_legend = []
    for table in tables:
        for name in table.legend:
            new_legend.append('-'.join([table.title, name]))
    new_rows = []

    for idx, table in enumerate(tables):
        for ridx, row in enumerate(table.rows):
            if idx == 0:
                new_rows.append([])
            new_rows[ridx].extend([row[col] for col in tables[0].legend])
    return ATable('-'.join([table.title for table in tables]),
            new_legend, new_rows)

def merge_vertical(tables):
    """Merge multiple tables into one tables vertically.

    Tables should have same legend.  If not, consider to use
    `compensate_columns()` first."""
    new_rows = []
    if len(tables) < 1:
        return None

    for table in tables:
        for row in table.rows:
            new_rows.append([row[col] for col in tables[0].legend])
    return ATable('-'.join([table.title for table in tables]),
            tables[0].legend, new_rows)

def split_with_key(table, keys):
    """Split a table into multiple tables with same keys.

    Title of each splitted tables will be the key.
    """
    inter_map = {}
    for row in table.rows:
        key = '-'.join([str(row[key]) for key in keys])
        if not inter_map.has_key(key):
            inter_map[key] = ATable(key, table.legend, [])
        inter_map[key].rows.append(row)
    return inter_map.values()

def __calc_stat(vals):
    minv = min(vals)
    maxv = max(vals)
    avg = sum(vals) / len(vals)
    variance = float(sum([pow(v - avg, 2) for v in vals])) / len(vals)
    stdev_ = math.sqrt(variance)
    return [avg, stdev_, minv, maxv]

def default_exclude_fn(col, val):
    return False

def calc_stat(table, keys, exclude_fn = default_exclude_fn):
    """Get average, min/max values, standard deviation of values in a table
    with same keys.
    """
    new_legend = []
    suffixes = ["_avg", "_stdev", "_min", "_max"]
    for name in table.legend:
        new_legend.extend([name + suffix for suffix in suffixes])
    new_legend.append("nr_samples")

    new_rows = []
    ret = ATable(table.title, new_legend, [])

    tables = split_with_key(table, keys)
    for subtable in tables:
        new_row = []
        new_rows.append(new_row)
        for col in subtable.legend:
            try:
                vals = [float(row[col]) for row in subtable.rows
                        if not exclude_fn(col, row[col])]
            except ValueError:
                val = subtable.rows[0][col]
                new_row.extend([val, val, val, val])
                continue
            if len(vals) == 0:
                val = subtable.rows[0][col]
                new_row.extend([val, val, val, val])
                continue
            new_row.extend(__calc_stat(vals))
        new_row.append(len(subtable.rows))
    raw_table = ATable(table.title, new_legend, new_rows)
    final_legend = []
    for suffix in suffixes:
        final_legend.extend([name + suffix for name in table.legend])
    final_legend.append("nr_samples")
    return pick_fields(raw_table, final_legend)

def sort_with(table, keys):
    for key in reversed(keys):
        table.rows.sort(key=lambda x: x[key])
    return table

def compensate(tables, key_col, default_val):
    """Compensate tables to have same keys.

    Rows in tables should be sorted by the key."""
    total_keys = []
    for table in tables:
        for row in table.rows:
            key = row[key_col]
            if not key in total_keys:
                total_keys.append(key)
    total_keys.sort()
    for table in tables:
        for idx, key in enumerate(total_keys):
            if len(table.rows) <= idx or table.rows[idx][key_col] != key:
                new_row = {col: default_val for col in table.legend}
                new_row[key_col] = key
                table.rows.insert(idx, new_row)

def compensate_columns(tables, default_val):
    """Compensate tables to have same columns."""
    unified_legend = []
    for table in tables:
        for name in table.legend:
            if not name in unified_legend:
                unified_legend.append(name)
    for table in tables:
        for name in unified_legend:
            if name in table.legend:
                continue
            for row in table.rows:
                row[name] = default_val
        table.legend = unified_legend
    return tables

if __name__ == "__main__":
    t = ATable("foo", ["key", "val", "something"],
            [
                [1, 1, 'a'], [1, 3, 'a'], [1, 5, 'a'],
                [2, 3, 'b'], [2,4,'b'], [2,5,'b'], [3, 5, 'c']])
    stat_calced = calc_stat(t, ["key"])
    sorted_ = sort_with(stat_calced, ["key_avg"])
    print t
    print sorted_
    print sorted_.csv()
    print from_csv(sorted_.csv())
    print sort_with(calc_stat(from_csv(t.csv()), ["key"]), ["key_avg"])

    t = ATable("foo", ["thrs", "system", "value1", "value2"], [
                [1, 'A', 10, 90],
                [2, 'A', 20, 80],
                [4, 'A', 30, 70],
                [1, 'B', 40, 60],
                [2, 'B', 50, 50],
                [4, 'B', 60, 40],
                [1, 'sys', 70, 30],
                [2, 'sys', 80, 20],
                [4, "sys", 90, 10],
            ])
    splits = split_with_key(t, ["system"])
    print merge(splits)
    print pick_fields(merge(splits).replace_legend("A-thrs", "thrs"),
            ["thrs", "A-value1", "B-value1", "A-value2", "B-value2"])

    t2 = t.append_column("avg", lambda x:
                        t.item_at(x, "value1") + t.item_at(x, "value2") / 2)
    print t2

    t = ATable("foo", ["key", "val"], [[1, 3], [3, 5], [5, 7]])
    t2 = ATable("bar", ["key", "val"], [[1, 3], [2, 4], [5, 7]])
    print t
    print t2
    compensate([t, t2], "key", -1)
    print "compensated"
    print t
    print t2

    t = ATable("foo", ["key", "val"], [[1, 3], [3, 5]])
    t.convert_column("key", lambda r: str(t.item_at(r, "val")))
    print t

    t = ATable("foo", ["key", "val"], [[1, 3], [2, 4]])
    t2 = ATable("foo2", ["key", "val"], [[3,3], [4,8]])
    print merge_vertical([t, t2])


    t3 = ATable("fooo", ["key", "val2"], [[3,4], [4,5]])
    compensate_columns([t, t3], -1)
    print "column compensated"
    print t
    print t3

    t = ATable("foo", ["key", "val"], [[1, 3], [1, 4], [1, 5], [2, 1], [2, 2]])
    stat = calc_stat(t, ["key"])
    stat = exclude_fields(stat,
            ["key_min", "key_max", "key_stdev", "key_nr_samples"])
    print stat

    t = from_human_readable_records(
"""Title


legend1
x1 val1
x2 val2


legend2
x1 val2-1
x2 val2-2
""")
    print "\n"
    print "human readable text test"
    print "========================"
    print ""
    print t
    print t.human_readable_txt()


    print "\n"
    print "normalization test"
    print "=================="
    print ""
    t = ATable("foo", ["key", "sysA", "sysB"], [[1, "3", "6"], [2, "4", "7"]])
    print t.normalize(1, [0])

    print "\n"
    print "format csv check test"
    print "====================="
    print ""
    if wrong_csv_format_check(
            """title, fooo
            leg1, leg2, leg3
            v1, v2, v3
            v4, v5, v6"""):
        print "FAIL"
        exit(1)

    if not wrong_csv_format_check(
            """titel, fooo
            leg1, leg2, leg3
            v1, v2, v3
            v4, v5, v6"""):
        print "FAIL"
        exit(1)

    if not wrong_csv_format_check(
            """title, fooo
            leg1, leg2, leg3
            v1, v2, v3
            v4, v5"""):
        print "FAIL"
        exit(1)
    if not wrong_csv_format_check(
            """title, fooo
            leg1, leg2, leg3
            v1, v2, v3
            v4, v5, v6
            """):
        print "FAIL"
        exit(1)

    print "PASS"

    print "\n"
    print "human readable text format check test"
    print "====================================="
    print ""
    if wrong_human_readable_txt(
            """Title


            legend1
            x1 val1
            x2 val2


            legend2
            x1 val2-1
            x2 val2-2
            """):
        print "FAIL"
        exit(1)
    if not wrong_human_readable_txt(
            """Title


            legend1
            x1 val1


            legend2
            x1 val2-1
            x2 val2-2
            """):
        print "FAIL"
        exit(1)
    if not wrong_human_readable_txt(
            """Title


            legend1
            x1 val1
            x2


            legend2
            x1 val2-1
            x2 val2-2
            """):
        print "FAIL"
        exit(1)
    if not wrong_human_readable_txt(
            """Title


            legend1
            x1 val1
            x2 val2


            legend2
            x1 val2-1
            x3 val2-2
            """):
        print "FAIL"
        exit(1)

    print "PASS"
