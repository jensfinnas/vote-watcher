import agate

def rename_column(table, old_name, new_name):
    column_type = table.columns[old_name].data_type
    table = table.compute([ (new_name, agate.Formula(column_type, lambda r: r[old_name])) ])
    column_names = list(table.column_names)
    column_names.remove(old_name)
    return table.select(column_names)