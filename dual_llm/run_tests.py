# test_runner.py
import unittest
from test_suite import TestMinDistance  # Updated to match the minDistance test suite

# Mapping of test methods to categories (based on the TestMinDistance test suite aligned with analysis result)
category_mapping = {
    # Category 1: Incorrect initialization of dp array
    'test_dp_initialization_case1': 'Category 1: Incorrect initialization of dp array',
    'test_dp_initialization_case2': 'Category 1: Incorrect initialization of dp array',
    'test_dp_initialization_case3': 'Category 1: Incorrect initialization of dp array',
    'test_dp_initialization_case4': 'Category 1: Incorrect initialization of dp array',

    # Category 2: Out of bounds error in dp array access
    'test_out_of_bounds_case1': 'Category 2: Out of bounds error in dp array access',
    'test_out_of_bounds_case2': 'Category 2: Out of bounds error in dp array access',
    'test_out_of_bounds_case3': 'Category 2: Out of bounds error in dp array access',
    'test_out_of_bounds_case4': 'Category 2: Out of bounds error in dp array access',

    # Category 3: Incorrect calculation of minimum operations
    'test_min_operations_case1': 'Category 3: Incorrect calculation of minimum operations',
    'test_min_operations_case2': 'Category 3: Incorrect calculation of minimum operations',
    'test_min_operations_case3': 'Category 3: Incorrect calculation of minimum operations',
    'test_min_operations_case4': 'Category 3: Incorrect calculation of minimum operations',

    # Category 4: Missing base case for when both strings are empty
    'test_empty_strings_case1': 'Category 4: Missing base case for when both strings are empty',
    'test_empty_strings_case2': 'Category 4: Missing base case for when both strings are empty',
    'test_empty_strings_case3': 'Category 4: Missing base case for when both strings are empty',
    'test_empty_strings_case4': 'Category 4: Missing base case for when both strings are empty',
}

# Mapping of categories to logical error types
logical_error_types = {
    'Category 1: Incorrect initialization of dp array': 'Error in initializing the dynamic programming array, leading to incorrect base cases for edit distance calculation (e.g., handling empty strings or initial rows/columns)',
    'Category 2: Out of bounds error in dp array access': 'Accessing the dp array out of bounds, causing index errors or incorrect edit distance calculations for strings of different lengths',
    'Category 3: Incorrect calculation of minimum operations': 'Incorrectly computing the minimum cost of insert, delete, or replace operations in the dp array, leading to wrong edit distance values',
    'Category 4: Missing base case for when both strings are empty': 'Failing to handle the base case where both input strings are empty, leading to incorrect or undefined edit distance results',
    'Unknown Category': 'Unknown logical error type',
}
# Helper function to flatten the test suite and get test method names
def get_all_test_names(suite):
    test_names = []
    for test in suite:
        if isinstance(test, unittest.TestCase):
            test_names.append(test._testMethodName)
        elif isinstance(test, unittest.TestSuite):
            test_names.extend(get_all_test_names(test))
    return test_names

# Run the tests and display results
if __name__ == '__main__':
    # Load and run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMinDistance)
    result = unittest.TestResult()
    suite.run(result)

    # Debug: Print all test names in the suite
    all_test_names = get_all_test_names(suite)
    print("Debug: All Test Names in Suite")
    for name in all_test_names:
        print(name)
    print(f"Total Loaded Tests: {len(all_test_names)}")
    print()

    # Print test results
    print("Test Results\n")

    # Print failed tests with logical error type
    print("Failed Tests:")
    failed_count = 0
    failed_test_names = set()  # Use a set to avoid duplicates
    for failure in result.failures + result.errors:
        failed_count += 1
        test_name = failure[0]._testMethodName
        failed_test_names.add(test_name)
        category = category_mapping.get(test_name, 'Unknown Category')
        error_type = logical_error_types.get(category, 'Unknown Logical Error')
        print(f"Test: {test_name}")
        print(f"Category: {category}")
        print(f"Status: Failed")
        print(f"Logical Error Type: {error_type}")
        print(f"Error Details: {failure[1].splitlines()[-1]}")
        print()

    if failed_count == 0:
        print("No failures.\n")

    # Print passed tests
    print("Passed Tests:")
    passed_count = 0
    expected_test_names = set(category_mapping.keys())  # All expected test names
    for test_name in expected_test_names:
        if test_name not in failed_test_names:
            passed_count += 1
            category = category_mapping.get(test_name, 'Unknown Category')
            print(f"Test: {test_name}")
            print(f"Category: {category}")
            print(f"Status: Passed")
            print()

    if passed_count == 0:
        print("No tests passed.\n")

    # Summary
    print("Summary")
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Total Reported: {passed_count + failed_count}")