import unittest
from test_suite import TestFindMedianSortedArrays

# Mapping of test methods to categories
category_mapping = {
    'test_empty_array_case1': 'Category 1: Incorrect handling of edge cases when one of the arrays is empty',
    'test_empty_array_case2': 'Category 1: Incorrect handling of edge cases when one of the arrays is empty',
    'test_empty_array_case3': 'Category 1: Incorrect handling of edge cases when one of the arrays is empty',
    'test_empty_array_case4': 'Category 1: Incorrect handling of edge cases when one of the arrays is empty',
    'test_even_total_length_case1': 'Category 2: Incorrect calculation of the median when the total length of the arrays is even',
    'test_even_total_length_case2': 'Category 2: Incorrect calculation of the median when the total length of the arrays is even',
    'test_even_total_length_case3': 'Category 2: Incorrect calculation of the median when the total length of the arrays is even',
    'test_even_total_length_case4': 'Category 2: Incorrect calculation of the median when the total length of the arrays is even',
    'test_median_not_midpoint_case1': 'Category 3: Incorrect handling of cases where the median is not at the midpoint of either array',
    'test_median_not_midpoint_case2': 'Category 3: Incorrect handling of cases where the median is not at the midpoint of either array',
    'test_median_not_midpoint_case3': 'Category 3: Incorrect handling of cases where the median is not at the midpoint of either array',
    'test_median_not_midpoint_case4': 'Category 3: Incorrect handling of cases where the median is not at the midpoint of either array',
    'test_odd_total_length_case1': 'Category 4: Incorrect calculation of the median when the total length of the arrays is odd',
    'test_odd_total_length_case2': 'Category 4: Incorrect calculation of the median when the total length of the arrays is odd',
    'test_odd_total_length_case3': 'Category 4: Incorrect calculation of the median when the total length of the arrays is odd',
    'test_odd_total_length_case4': 'Category 4: Incorrect calculation of the median when the total length of the arrays is odd',
}

# Mapping of categories to logical error types
logical_error_types = {
    'Category 1: Incorrect handling of edge cases when one of the arrays is empty': 'Incorrect handling of edge cases when one of the arrays is empty',
    'Category 2: Incorrect calculation of the median when the total length of the arrays is even': 'Incorrect calculation of the median when the total length of the arrays is even',
    'Category 3: Incorrect handling of cases where the median is not at the midpoint of either array': 'Incorrect handling of cases where the median is not at the midpoint of either array',
    'Category 4: Incorrect calculation of the median when the total length of the arrays is odd': 'Incorrect calculation of the median when the total length of the arrays is odd',
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFindMedianSortedArrays)
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