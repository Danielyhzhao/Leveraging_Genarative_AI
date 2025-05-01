import unittest
from code_input import Solution  # Assuming Solution class has the minDistance method

class TestMinDistance(unittest.TestCase):
    def setUp(self):
        """Initialize a Solution instance before each test."""
        self.solution = Solution()

    # Category 1: Incorrect initialization of dp array
    def test_dp_initialization_case1(self):
        """Test case: word1 = 'a', word2 = 'b', Expected: 1"""
        word1 = "a"
        word2 = "b"
        expected = 1
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_dp_initialization_case2(self):
        """Test case: word1 = 'ab', word2 = 'c', Expected: 2"""
        word1 = "ab"
        word2 = "c"
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_dp_initialization_case3(self):
        """Test case: word1 = '', word2 = 'abc', Expected: 3"""
        word1 = ""
        word2 = "abc"
        expected = 3
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_dp_initialization_case4(self):
        """Test case: word1 = 'abc', word2 = '', Expected: 3"""
        word1 = "abc"
        word2 = ""
        expected = 3
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    # Category 2: Out of bounds error in dp array access
    def test_out_of_bounds_case1(self):
        """Test case: word1 = 'a', word2 = 'bc', Expected: 2"""
        word1 = "a"
        word2 = "bc"
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_out_of_bounds_case2(self):
        """Test case: word1 = 'ab', word2 = 'cd', Expected: 2"""
        word1 = "ab"
        word2 = "cd"
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_out_of_bounds_case3(self):
        """Test case: word1 = 'abc', word2 = 'd', Expected: 3"""
        word1 = "abc"
        word2 = "d"
        expected = 3
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_out_of_bounds_case4(self):
        """Test case: word1 = 'a', word2 = 'bcd', Expected: 3"""
        word1 = "a"
        word2 = "bcd"
        expected = 3
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    # Category 3: Incorrect calculation of minimum operations
    def test_min_operations_case1(self):
        """Test case: word1 = 'ab', word2 = 'ba', Expected: 2"""
        word1 = "ab"
        word2 = "ba"
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_min_operations_case2(self):
        """Test case: word1 = 'abc', word2 = 'bca', Expected: 2"""
        word1 = "abc"
        word2 = "bca"
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_min_operations_case3(self):
        """Test case: word1 = 'abcd', word2 = 'dcba', Expected: 4"""
        word1 = "abcd"
        word2 = "dcba"
        expected = 4
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_min_operations_case4(self):
        """Test case: word1 = 'abcde', word2 = 'edcba', Expected: 4"""
        word1 = "abcde"
        word2 = "edcba"
        expected = 4
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    # Category 4: Missing base case for when both strings are empty
    def test_empty_strings_case1(self):
        """Test case: word1 = '', word2 = '', Expected: 0"""
        word1 = ""
        word2 = ""
        expected = 0
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_empty_strings_case2(self):
        """Test case: word1 = 'a', word2 = '', Expected: 1"""
        word1 = "a"
        word2 = ""
        expected = 1
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_empty_strings_case3(self):
        """Test case: word1 = '', word2 = 'a', Expected: 1"""
        word1 = ""
        word2 = "a"
        expected = 1
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

    def test_empty_strings_case4(self):
        """Test case: word1 = 'ab', word2 = '', Expected: 2"""
        word1 = "ab"
        word2 = ""
        expected = 2
        result = self.solution.minDistance(word1, word2)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()