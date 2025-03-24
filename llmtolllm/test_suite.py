import unittest
from code_input import Solution

class TestFindMedianSortedArrays(unittest.TestCase):
    def setUp(self):
        """Initialize a Solution instance before each test."""
        self.solution = Solution()

    # Category 1: Incorrect handling of edge cases when one of the arrays is empty
    def test_empty_array_case1(self):
        """Test case: nums1 = [1, 2, 3], nums2 = []"""
        nums1 = [1, 2, 3]
        nums2 = []
        expected = 2.0  # Median of [1, 2, 3] is 2.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_empty_array_case2(self):
        """Test case: nums1 = [], nums2 = [1, 2, 3]"""
        nums1 = []
        nums2 = [1, 2, 3]
        expected = 2.0  # Median of [1, 2, 3] is 2.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_empty_array_case3(self):
        """Test case: nums1 = [1], nums2 = []"""
        nums1 = [1]
        nums2 = []
        expected = 1.0  # Median of [1] is 1.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_empty_array_case4(self):
        """Test case: nums1 = [], nums2 = [1]"""
        nums1 = []
        nums2 = [1]
        expected = 1.0  # Median of [1] is 1.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    # Category 2: Incorrect calculation of the median when the total length of the arrays is even
    def test_even_total_length_case1(self):
        """Test case: nums1 = [1, 2], nums2 = [3, 4]"""
        nums1 = [1, 2]
        nums2 = [3, 4]
        expected = 2.5  # Merged: [1, 2, 3, 4], median = (2 + 3) / 2 = 2.5
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_even_total_length_case2(self):
        """Test case: nums1 = [1, 3], nums2 = [2, 4]"""
        nums1 = [1, 3]
        nums2 = [2, 4]
        expected = 2.5  # Merged: [1, 2, 3, 4], median = (2 + 3) / 2 = 2.5
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_even_total_length_case3(self):
        """Test case: nums1 = [1, 2, 3, 4], nums2 = []"""
        nums1 = [1, 2, 3, 4]
        nums2 = []
        expected = 2.5  # Merged: [1, 2, 3, 4], median = (2 + 3) / 2 = 2.5
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_even_total_length_case4(self):
        """Test case: nums1 = [], nums2 = [1, 2, 3, 4]"""
        nums1 = []
        nums2 = [1, 2, 3, 4]
        expected = 2.5  # Merged: [1, 2, 3, 4], median = (2 + 3) / 2 = 2.5
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    # Category 3: Incorrect handling of cases where the median is not at the midpoint of either array
    def test_median_not_midpoint_case1(self):
        """Test case: nums1 = [1, 3, 5], nums2 = [2, 4]"""
        nums1 = [1, 3, 5]
        nums2 = [2, 4]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_median_not_midpoint_case2(self):
        """Test case: nums1 = [1, 2, 3], nums2 = [4, 5]"""
        nums1 = [1, 2, 3]
        nums2 = [4, 5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_median_not_midpoint_case3(self):
        """Test case: nums1 = [1, 2], nums2 = [3, 4, 5]"""
        nums1 = [1, 2]
        nums2 = [3, 4, 5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_median_not_midpoint_case4(self):
        """Test case: nums1 = [1, 2, 3], nums2 = [4]"""
        nums1 = [1, 2, 3]
        nums2 = [4]
        expected = 2.5  # Merged: [1, 2, 3, 4], median = (2 + 3) / 2 = 2.5
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    # Category 4: Incorrect calculation of the median when the total length of the arrays is odd
    def test_odd_total_length_case1(self):
        """Test case: nums1 = [1, 2, 3], nums2 = [4, 5]"""
        nums1 = [1, 2, 3]
        nums2 = [4, 5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_odd_total_length_case2(self):
        """Test case: nums1 = [1, 2], nums2 = [3, 4, 5]"""
        nums1 = [1, 2]
        nums2 = [3, 4, 5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_odd_total_length_case3(self):
        """Test case: nums1 = [1, 2, 3, 4], nums2 = [5]"""
        nums1 = [1, 2, 3, 4]
        nums2 = [5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

    def test_odd_total_length_case4(self):
        """Test case: nums1 = [1], nums2 = [2, 3, 4, 5]"""
        nums1 = [1]
        nums2 = [2, 3, 4, 5]
        expected = 3.0  # Merged: [1, 2, 3, 4, 5], median = 3.0
        result = self.solution.findMedianSortedArrays(nums1, nums2)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()