from typing import List

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        len1 = len(nums1)
        len2 = len(nums2)
        if ((len1 + len2) % 2 == 1):
            if (len1 % 2 == 1 and nums1[int((len1 - 1) / 2)] >= nums2[int(len2 / 2)]):
                return nums1[int((len1 - 1) / 2)]
            elif (len2 % 2 == 1 and nums2[int((len2 - 1) / 2)] >= nums1[int(len1 / 2)]):
                return nums2[int((len2 - 1) / 2)]
            else:
                if (len1 % 2 == 1):
                    return nums1[int((len1 - 1) / 2)]
                else:
                    return nums2[int((len2 - 1) / 2)]
        elif ((len1 + len2) % 2 == 0):
            if (len1 % 2 == 1 and len2 % 2 == 1):
                if (nums1[int((len1 - 1) / 2)] >= nums2[int((len2 - 1) / 2)]):
                    if (nums1[int((len1 - 1) / 2)] >= nums2[int(len2 / 2)]):
                        return (nums1[int((len1 - 1) / 2)] + nums2[int((len2 - 1) / 2)]) / 2
                    else:
                        return (nums1[int((len1 - 1) / 2)] + nums2[int(len2 / 2)]) / 2
                else:
                    if (nums2[int((len2 - 1) / 2)] >= nums1[int(len1 / 2)]):
                        return (nums1[int(len1 / 2)] + nums2[int((len2 - 1) / 2)]) / 2
                    else:
                        return (nums1[int(len1 / 2)] + nums2[int(len1 / 2)]) / 2
            else:
                if (nums1[int(len1 / 2)] >= nums2[int(len2 / 2) - 1]):
                    if (nums1[int(len1 / 2)] >= nums2[int(len2 / 2)]):
                        return (nums1[int(len1 / 2) - 1] + nums1[int(len1 / 2)]) / 2
                    else:
                        return (nums1[int(len1 / 2) - 1] + nums2[int(len2 / 2)]) / 2
                else:
                    if (nums2[int(len2 / 2)] >= nums1[int(len1 / 2) - 1]):
                        return (nums2[int(len2 / 2) - 1] + nums2[int(len2 / 2)]) / 2