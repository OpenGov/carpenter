# This import fixes sys.path issues
import parentpath

import unittest
import os
from os.path import dirname
from carpenter.carpenter import (
    stitch_block,
    stitch_block_rows,
    append_column,
    insert_column,
    remove_column,
    fill_block_blanks,
    split_block_by_row_length)
from datawrap import tableloader

class CarpenterTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(dirname(__file__), 'table_data')
        self.names_table = tableloader.read(os.path.join(self.data_dir, "names_table.xlsx"))[0].load()

    def test_stich_blocks(self):
        block_one_rows = 20
        block_one_columns = 10
        block_one = [[1 for jj in range(block_one_columns)] for ii in range(block_one_rows)]
        block_two_rows = 15
        block_two_columns = 15
        blockTwo = [[2 for jj in range(block_two_columns)] for ii in range(block_two_rows)]

        stiched = stitch_block([block_one, blockTwo])
        self.assertEquals(len(stiched), max(block_one_rows, block_two_rows))
        self.assertEquals(len(stiched[0]), block_one_columns + block_two_columns)
        for row in range(block_one_rows):
            for col in range(block_one_columns):
                self.assertEquals(stiched[row][col], 1)

        for row in range(block_one_rows, max(block_one_rows, block_two_rows)):
            for col in range(block_one_columns):
                self.assertEquals(stiched[row][col], None)

        for row in range(block_two_rows):
            for col in range(block_one_columns, block_one_columns + block_two_columns):
                self.assertEquals(stiched[row][col], 2)

        for row in range(block_two_rows, max(block_one_rows, block_two_rows)):
            for col in range(block_one_columns, block_one_columns + block_two_columns):
                self.assertEquals(stiched[row][col], None)

    def test_stich_row_blocks(self):
        block_one_rows = 20
        block_one_columns = 10
        block_one = [[1 for jj in range(block_one_columns)] for ii in range(block_one_rows)]
        block_two_rows = 15
        block_two_columns = 15
        blockTwo = [[2 for jj in range(block_two_columns)] for ii in range(block_two_rows)]

        stiched = stitch_block_rows([block_one, blockTwo])
        self.assertEquals(len(stiched), block_one_rows + block_two_rows)
        self.assertEquals(len(stiched[0]), max(block_one_columns, block_two_columns))
        for row in range(block_one_rows):
            for col in range(block_one_columns):
                self.assertEquals(stiched[row][col], 1)
            for col in range(block_one_columns, block_two_columns):
                self.assertEquals(stiched[row][col], None)

        for row in range(block_one_rows, block_one_rows + block_two_rows):
            for col in range(block_two_columns):
                self.assertEquals(stiched[row][col], 2)

    def test_add_remove_columns(self):
        prior_len = len(self.names_table[0])
        append_column(self.names_table, "Blank")
        self.assertEquals(len(self.names_table[0]) - 1, prior_len)
        self.assertEquals(self.names_table[0][-1], "Blank")
        for row in self.names_table[1:]:
            self.assertEquals(row[-1], None)

        prior_len = len(self.names_table[0])
        insert_column(self.names_table, 0)
        self.assertEquals(len(self.names_table[0])-1, prior_len)
        for row in self.names_table:
            self.assertEquals(row[0], None)

        prior_len = len(self.names_table[0])
        insert_column(self.names_table, "Blank", "Pre-Blank")
        self.assertEquals(len(self.names_table[0]) - 1, prior_len)
        self.assertEquals(self.names_table[0][-2], "Pre-Blank")
        for row in self.names_table[1:]:
            self.assertEquals(row[-2], None)

        prior_len = len(self.names_table[0])
        insert_column(self.names_table, prior_len, "End", prior_len)
        self.assertEquals(len(self.names_table[0]) - 1, prior_len)
        self.assertEquals(self.names_table[0][-1], "End")
        for row in self.names_table[1:]:
            self.assertEquals(row[-1], prior_len)

        prior_len = len(self.names_table[0])
        remove_column(self.names_table, len(self.names_table[0]) - 1)
        self.assertEquals(len(self.names_table[0]), prior_len - 1)
        self.assertEquals(self.names_table[0][-1], "Blank")
        for row in self.names_table[1:]:
            self.assertEquals(row[-1], None)

    def test_split_blocks(self):
        block = [
            [1, 2, 3, None],
            ['a', 'b', 'c', 'd'],
            [None, 'a'],
            ['a little longer cell'],
            [1, 2, 3, 4],
            [None],
        ]

        self.assertListEqual([block], split_block_by_row_length(block, 0))
        self.assertListEqual([
                [
                    [1, 2, 3, None],
                    ['a', 'b', 'c', 'd'],
                    [None, 'a']
                ],
                [['a little longer cell']],
                [[1, 2, 3, 4]],
                [[None]],
            ],
            split_block_by_row_length(block, 1))
        self.assertListEqual([
                [
                    [1, 2, 3, None],
                    ['a', 'b', 'c', 'd']],
                [[None, 'a']],
                [['a little longer cell']],
                [[1, 2, 3, 4]],
                [[None]],
            ],
            split_block_by_row_length(block, 2))
        self.assertListEqual([
                [[1, 2, 3, None]],
                [['a', 'b', 'c', 'd']],
                [[None, 'a']],
                [['a little longer cell']],
                [[1, 2, 3, 4]],
                [[None]],
            ],
            split_block_by_row_length(block, 3))
        self.assertListEqual([
                [[1, 2, 3, None]],
                [['a', 'b', 'c', 'd']],
                [[None, 'a']],
                [['a little longer cell']],
                [[1, 2, 3, 4]],
                [[None]],
            ],
            split_block_by_row_length(block, 4))

    def test_fill_block_blanks(self):
        block = [
            ['a', None, '', 0],
            ['testing', 'more', 'things'],
            []
        ]

        self.assertEqual([
                ['a', 'FILL', 'FILL', 0],
                ['testing', 'more', 'things'],
                []
            ],
            fill_block_blanks(block, 'FILL'))

if __name__ == "__main__":
    unittest.main()
