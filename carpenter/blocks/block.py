# This import fixes sys.path issues
import parentpath

import re
from flagable import Flagable
from cellanalyzer import is_empty_cell, is_text_cell, is_num_cell, get_cell_type, check_cell_type
from datawrap.tablewrap import TableTranspose
from carpenter.regex import allregex

class InvalidBlockError(ValueError):
    '''
    Indicator for an Invalid Block during initialization.
    '''
    pass

class TableBlock(Flagable):
    '''
    Represents a sub-table of a data file worksheet. This provides
    functionality for converting to row-titled tables for exporting
    to csv files.
    '''
    def __init__(self, table_conversion, used_cells, block_start, block_end, 
                 worksheet=None, flags=None, units=None, complete_block=False):
        '''
        Constructor throws an InvalidBlockError if the block is not
        valid or convertible to a valid configuration.
        
        Args:
            complete_block: Tells the validator to assume every cell is
                filled in the block, which speeds up checks
        '''
        self.table = table_conversion
        self.used = used_cells
        self.start = block_start
        self.end = block_end
        self.complete_block = complete_block
        self.flags = flags if flags != None else {}
        self.units = units if units != None else {}
        self.worksheet = worksheet
        validator = BlockValidator(self.table, self.worksheet, 
                                   self.flags, self.used,
                                   self.start, self.end,
                                   complete_block=self.complete_block)
        if not validator.validate_block():
            raise InvalidBlockError()
        
    def _find_titles(self, row_index, column_index):
        '''
        Helper method to find all titles for a particular cell.
        '''
        titles = []
        
        for column_search in range(self.start[1], column_index):
            cell = self.table[row_index][column_search]
            if cell == None or (isinstance(cell, basestring) and not cell):
                continue
            elif isinstance(cell, basestring):
                titles.append(cell)
            else:
                break
        
        for row_search in range(self.start[0], row_index):
            cell = self.table[row_search][column_index]
            if cell == None or (isinstance(cell, basestring) and not cell):
                continue
            elif isinstance(cell, basestring):
                titles.append(cell)
            else:
                break
            
        return titles
    
    def copy_raw_block(self):
        '''
        Copies the block as it was originally specified by start and
        end into a new table.
        
        Returns:
            A copy of the block with no block transformations.
        '''
        ctable = []
        r, c = 0, 0
        try:
            for row_index in range(self.start[0], self.end[0]):
                r = row_index
                row = []
                ctable.append(row)
                for column_index in range(self.start[1], self.end[1]):
                    c = column_index
                    row.append(self.table[row_index][column_index])
        except IndexError:
            raise InvalidBlockError('Missing table element at [%d, %d]' % (r, c))
        return ctable
    
    def copy_numbered_block(self):
        '''
        Copies the block as it was originally specified by start and
        end into a new table. Additionally inserts the original table
        indices in the first row of the block.
        
        Returns:
            A copy of the block with no block transformations.
        '''
        raw_block = self.copy_raw_block()
        # Inserts the column number in row 0
        raw_block.insert(0, range(self.start[1], self.end[1]))
        return raw_block
        
    def convert_to_row_table(self, add_units=True):
        '''
        Converts the block into row titled elements. These elements are
        copied into the return table, which can be much longer than the
        original block.
        
        Args:
            add_units: Indicates if units should be appened to each row item.
        
        Returns:
            A row-titled table representing the data in the block.
        '''
        rtable = []
        if add_units:
            relavent_units = self.get_relavent_units()
        
        # Create a row for each data element
        for row_index in range(self.start[0], self.end[0]):
            for column_index in range(self.start[1], self.end[1]):
                cell = self.table[row_index][column_index]
                if cell != None and isinstance(cell, (int, float)):
                    titles = self._find_titles(row_index, column_index)
                    titles.append(cell)
                    if add_units:
                        titles.append(relavent_units.get((row_index, column_index)))
                    rtable.append(titles)
                    
        # If we had all 'titles', just return the original block
        if not rtable:
            for row_index in range(self.start[0], self.end[0]):
                row = []
                rtable.append(row)
                for column_index in range(self.start[1], self.end[1]):
                    row.append(self.table[row_index][column_index])
                if add_units:
                    row.append(relavent_units.get((row_index, column_index)))
                
        return rtable
    
    def flag_is_related(self, flag):
        '''
        Checks for relationship between a flag and this block.
        
        Returns:
            True if the flag is related to this block.
        '''
        same_worksheet = flag.worksheet == self.worksheet
        if isinstance(flag.location, (tuple, list)):
            return (flag.location[0] >= self.start[0] and flag.location[0] < self.end[0] and
                    flag.location[1] >= self.start[1] and flag.location[1] < self.end[1] and
                    same_worksheet)
        else:
            return same_worksheet
        
    def unit_is_related(self, location, worksheet):
        '''
        Checks for relationship between a unit location and this block.
        
        Returns:
            True if the location is related to this block.
        '''
        same_worksheet = worksheet == self.worksheet
        if isinstance(location, (tuple, list)):
            return (location[0] >= self.start[0] and location[0] < self.end[0] and
                    location[1] >= self.start[1] and location[1] < self.end[1] and
                    same_worksheet)
        else:
            return same_worksheet
    
    def get_relavent_flags(self):
        '''
        Retrieves the relevant flags for this data block.
        
        Returns:
            All flags related to this block.
        '''
        relavent_flags = {}
        
        for code, flags_list in self.flags.items():
            relavent_flags[code] = []
            for flag in flags_list:
                if self.flag_is_related(flag):
                    relavent_flags[code].append(flag)
            # Remove that flag level if no error exists
            if not relavent_flags[code]:
                del relavent_flags[code]
                
        return relavent_flags
    
    def get_relavent_units(self):
        '''
        Retrieves the relevant units for this data block.
        
        Returns:
            All flags related to this block.
        '''
        relavent_units = {}
        
        for location,unit in self.units.items():
            if self.unit_is_related(location, self.worksheet):
                relavent_units[location] = unit
                
        return relavent_units
    
    def get_worst_flag_level(self):
        '''
        Determines the worst flag present in the provided flags. If no
        flags are given then a 'minor' value is returned.
        
        No argument version of parent function.
        '''
        return Flagable.get_worst_flag_level(self, self.get_relavent_flags())

class BlockValidator(Flagable):
    '''
    The block validator checks and repairs the defined block within a
    table. The validate method performs the check and repair process.
    If the block cannot be repaired then validate will return false.
    
    The validation process is fairly complicated to catch all edge
    cases correctly. There are inherent structures within data sets
    which have implied meaning. These implied states are converted
    when detected. Others are ambiguous and a common case decision
    is made or the valid return is set to False.
    '''
    def __init__(self, table, worksheet, flags, used_cells, 
                 block_start, block_end, complete_block=False):
        self.table = table
        self.worksheet = worksheet
        self.flags = flags
        self.used_cells = used_cells
        self.start = block_start
        self.end = block_end
        self.complete_block = complete_block
        
    def validate_block(self):
        '''
        This method is a multi-stage process which repairs row titles, then
        repairs column titles, then checks for invalid rows, and finally
        for invalid columns.
        
        This maybe should have been written via state machines... Also suggested
        as being possibly written with code-injection.
        '''
        # Don't allow for 0 width or 0 height blocks
        if self._check_zero_size():
            return False
        # Single width or height blocks should be considered
        self._check_one_size()
        
        # Repair any obvious block structure issues
        self._repair_row()
        self._repair_column()
        
        # Fill any remaining empty titles if we're not a complete block
        if not self.complete_block:
            self._fill_row_holes()
            self._fill_column_holes()
        
        # Check for invalid data after repairs
        self._validate_rows()
        self._validate_columns()
        
        # We're valid enough to be used -- though error flags may have
        # been thrown into flags.
        return True
    
    def _check_zero_size(self):
        '''
        Checks for zero height or zero width blocks and flags the occurrence.
        
        Returns:
            True if the block is size 0.
        '''
        block_zero = self.end[0] <= self.start[0] or self.end[1] <= self.start[1]
        if block_zero:
            self.flag_change(self.flags, 'fatal', worksheet=self.worksheet, 
                             message=self.FLAGS['0-size'])
        return block_zero
    
    def _check_one_size(self):
        '''
        Checks for single height or single width blocks and flags the occurrence.
        
        Returns:
            True if the block is size 1.
        '''
        block_one = self.end[0] == self.start[0]+1 or self.end[1] == self.start[1]+1
        if block_one:
            self.flag_change(self.flags, 'error', self.start, self.worksheet, 
                             message=self.FLAGS['1-size'])
        return block_one
    
    def _repair_row(self):
        '''
        Searches for missing titles that can be inferred from the
        surrounding data and automatically repairs those titles.
        '''
        # Repair any title rows
        check_for_title = True
        for row_index in range(self.start[0], self.end[0]):
            table_row = self.table[row_index]
            row_start = table_row[self.start[1]]
            
            # Look for empty cells leading titles
            if check_for_title and is_empty_cell(row_start):
                self._stringify_row(row_index)
            # Check for year titles in column or row
            elif (isinstance(row_start, basestring) and 
                  re.search(allregex.year_regex, row_start)):
                self._check_stringify_year_row(row_index)
            else:
                check_for_title = False
                 
    def _repair_column(self):
        '''
        Same as _repair_row but for columns.
        ''' 
        # Repair any title columns
        check_for_title = True
        for column_index in range(self.start[1], self.end[1]):
            table_column = TableTranspose(self.table)[column_index]
            column_start = table_column[self.start[0]]
            
            # Only iterate through columns starting with a blank cell
            if check_for_title and is_empty_cell(column_start):
                self._stringify_column(column_index)
            # Check for year titles in column or row
            elif (isinstance(column_start, basestring) and 
                  re.search(allregex.year_regex, column_start)):
                self._check_stringify_year_column(column_index)
            else:
                check_for_title = False
    
    def _fill_row_holes(self):
        '''
        Fill any remaining row title cells that are empty.
        This must be done after the other passes to avoid 
        preemptively filling in empty cells reserved for 
        other operations.
        
        TODO potential optimization, mark rows/columns that
        were already processed and skip them here.
        ''' 
        for row_index in range(self.start[0], self.end[0]):
            table_row = self.table[row_index]
            row_start = table_row[self.start[1]]
            if is_text_cell(row_start):
                self._check_fill_title_row(row_index)
        
    def _fill_column_holes(self):
        '''
        Same as _fill_row_holes but for columns.
        ''' 
        for column_index in range(self.start[1], self.end[1]):
            table_column = TableTranspose(self.table)[column_index]
            column_start = table_column[self.start[0]]
            if is_text_cell(column_start):
                self._check_fill_title_column(column_index)
    
    def _validate_rows(self):
        '''
        Checks for any missing data row by row. It also checks for
        changes in cell type and flags multiple switches as an error.
        '''
        for row_index in range(self.start[0], self.end[0]):
            table_row = self.table[row_index]
            used_row = self.used_cells[row_index]
            
            row_type = None
            if self.end[1] > self.start[1]:
                row_type = get_cell_type(table_row[self.start[1]])
                
            num_type_changes = 0
            for column_index in range(self.start[1], self.end[1]):
                if used_row[column_index]:
                    self.flag_change(self.flags, 'error', (row_index, column_index), 
                                     self.worksheet, self.FLAGS['used'])
                if not check_cell_type(table_row[column_index], row_type):
                    row_type = get_cell_type(table_row[column_index])
                    num_type_changes += 1
                if num_type_changes > 1:
                    self.flag_change(self.flags, 'warning', (row_index, column_index-1), 
                                     self.worksheet, self.FLAGS['unexpected-change'])
                    # Decrement this to catch other cells which change again
                    num_type_changes -= 1
                # Mark this cell as used
                used_row[column_index] = True
               
    def _validate_columns(self):
        '''
        Same as _validate_rows but for columns. Also ignore used_cells as
        _validate_rows should update used_cells.
        '''  
        for column_index in range(self.start[1], self.end[1]):
            table_column = TableTranspose(self.table)[column_index]
            
            column_type = None
            if self.end[0] > self.start[0]:
                column_type = get_cell_type(table_column[self.start[0]])
                    
            num_type_changes = 0
            for row_index in range(self.start[0], self.end[0]):
                if not check_cell_type(table_column[row_index], column_type):
                    column_type = get_cell_type(table_column[row_index])
                    num_type_changes += 1
                if num_type_changes > 1:
                    self.flag_change(self.flags, 'warning', (row_index-1, column_index), 
                                     self.worksheet, self.FLAGS['unexpected-change'])
                    # Decrement this to catch other cells which change again
                    num_type_changes -= 1
        
    def _stringify_row(self, row_index):
        '''
        Stringifies an entire row, filling in blanks with prior titles as they
        are found.
        '''
        table_row = self.table[row_index]
        prior_cell = None
        for column_index in range(self.start[1], self.end[1]):
            cell, changed = self._check_interpret_cell(table_row[column_index], prior_cell, row_index, column_index)
            if changed:
                table_row[column_index] = cell
            prior_cell = cell
            
    def _stringify_column(self, column_index):
        '''
        Same as _stringify_row but for columns.
        ''' 
        table_column = TableTranspose(self.table)[column_index]
        prior_cell = None
        for row_index in range(self.start[0], self.end[0]):
            cell, changed = self._check_interpret_cell(table_column[row_index], prior_cell, row_index, column_index)
            if changed:
                table_column[row_index] = cell
            prior_cell = cell
            
    def _check_interpret_cell(self, cell, prior_cell, row_index, column_index):
        '''
        Helper function which checks cell type and performs cell translation to
        strings where necessary.
        
        Returns:
            A tuple of the form '(cell, changed)' where 'changed' indicates if 
            'cell' differs from input.
        '''
        changed = False
        if (not is_empty_cell(cell) and
            not is_text_cell(cell)):
            self.flag_change(self.flags, 'interpreted', (row_index, column_index), 
                             self.worksheet, self.FLAGS['converted-to-string'])
            cell = str(cell)
            changed = True
        # If we find a blank cell, propagate the prior title
        elif is_empty_cell(cell):
            self.flag_change(self.flags, 'interpreted', (row_index, column_index), 
                             self.worksheet, self.FLAGS['copied-title'])
            cell = prior_cell
            changed = True
        return cell, changed
    
    def _check_fill_title_row(self, row_index):
        '''
        Checks the given row to see if it is all titles and fills any
        blanks cells if that is the case.
        '''
        table_row = self.table[row_index]
        # Determine if the whole row is titles
        prior_row = self.table[row_index-1] if row_index > 0 else table_row
        for column_index in range(self.start[1], self.end[1]):
            if is_num_cell(table_row[column_index]) or is_num_cell(prior_row[column_index]):
                return
        # Since we're a title row, stringify the row
        self._stringify_row(row_index)
    
    def _check_fill_title_column(self, column_index):
        '''
        Same as _check_fill_title_row but for columns.
        ''' 
        # Determine if the whole column is titles
        table_column = TableTranspose(self.table)[column_index]
        prior_column = TableTranspose(self.table)[column_index-1] if column_index > 0 else table_column
        for row_index in range(self.start[0], self.end[0]):
            if is_num_cell(table_column[row_index]) or is_num_cell(prior_column[row_index]):
                return
        # Since we're a title row, stringify the column
        self._stringify_column(column_index)
    
    def _check_stringify_year_row(self, row_index):
        '''
        Checks the given row to see if it is labeled year data and fills
        any blank years within that data.
        '''
        table_row = self.table[row_index]
        # State trackers
        prior_year = None
        increasing_years = None
        for column_index in range(self.start[1]+1, self.end[1]):
            current_year = table_row[column_index]
            # Quit if we see 
            if not self._check_years(current_year, prior_year):
                return
            # Only copy when we see a non-empty entry
            if current_year:
                prior_year = current_year
            
        # If we have a title of years, convert them to strings
        self._stringify_row(row_index)
    
    def _check_stringify_year_column(self, column_index):
        '''
        Same as _check_stringify_year_row but for columns.
        '''  
        table_column = TableTranspose(self.table)[column_index]
        # State trackers
        prior_year = None
        increasing_years = None
        for row_index in range(self.start[0]+1, self.end[0]):
            current_year = table_column[row_index]
            if not self._check_years(current_year, prior_year):
                return
            # Only copy when we see a non-empty entry
            if current_year:
                prior_year = current_year
            
        # If we have a title of years, convert them to strings
        self._stringify_column(column_index)
    
    def _check_years(self, cell, prior_year):
        '''
        Helper method which defines the rules for checking for
        existence of a year indicator. If the cell is blank then
        prior_year is used to determine validity.
        '''
        # Anything outside these values shouldn't auto
        # categorize to strings
        min_year = 1900
        max_year = 2100

        # Empty cells could represent the prior cell's title,
        # but an empty cell before we find a year is not a title
        if is_empty_cell(cell):
            return bool(prior_year)
        # Check if we have a numbered cell between min and max years
        return is_num_cell(cell) and cell > min_year and cell < max_year
