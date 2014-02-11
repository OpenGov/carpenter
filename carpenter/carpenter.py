
def append_column(table, col_name, default_value=None):
    '''
    Appends a column to the raw data without any integrity checks.

    Args:
        default_value: The value which will assigned, not copied into each row
    '''
    table[0].append(col_name.strip())
    for row in table[1:]:
        row.append(default_value)

def remove_column(table, remove_index):
        '''
        Removes the specified column from the table.
        '''
        for row_index in range(len(table)):
            old_row = table[row_index]
            new_row = []
            for column_index in range(len(old_row)):
                if column_index != remove_index:
                    new_row.append(old_row[column_index])
            table[row_index] = new_row
        return table

# TODO change to preceding_column
def insert_column(table, following_col, col_name=None, default_value=None):
    '''
    Inserts a new column before another specified column (by name or index).

    Args:
        following_col: The column index or first row name where the insertion should occur
        col_name: The name to insert into the first row of the column. Leaving this argument
            to the default of None will apply the default_value to that row's cell.
        default_value: Can be a value or function which takes (row, index, value) as
            arguments to return a value.
    '''
    column_labels = table[0]
    following_index = 0

    def set_cell(row, column_index, value):
        # Allow function calls
        if hasattr(value, '__call__'):
            row[column_index] = value(column_labels, row, column_index)
        else:
            row[column_index] = value

    if isinstance(following_col, basestring):
        following_col = following_col.strip()
        for column_index in range(len(column_labels)):
            if column_labels[column_index] == following_col:
                following_index = column_index
                break
    else:
        following_index = following_col

    col_data_start = 0
    if col_name != None:
        table[0].insert(following_index, col_name.strip())
        col_data_start = 1
    for row in table[col_data_start:]:
        row.insert(following_index, None)
        if default_value:
            set_cell(row, min(following_index, len(row)-1), default_value)

def stitch_block(block_list):
    '''
    Stitches blocks together into a single block. These blocks are 2D tables
    usually generated from tableproc. The final block will be of dimensions
    (max(num_rows), sum(num_cols)).
    '''
    block_out = [[]]
    for block in block_list:
        num_row = len(block)
        row_len = len(block[0])
        if len(block_out) < num_row:
            for i in range(num_row-len(block_out)):
                block_out.append([None]*len(block_out[0]))
        for row_out, row_in in zip(block_out, block):
            row_out.extend(row_in)
        if len(block_out) > num_row:
            for row_out in block_out[num_row:]:
                row_out.extend([None]*row_len)
    return block_out
