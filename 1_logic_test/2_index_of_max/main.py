"""
เขียบนโปรแกรมหา index ของตัวเลขที่มีค่ามากที่สุดใน list

[Input]
numbers: list of numbers

[Output]
index: index of maximum number in list

[Example 1]
input = [1,2,1,3,5,6,4]
output = 5

[Example 2]
input = []
output = list can not blank
"""


class Solution:

    def find_max_index(self, numbers: list) -> int | str:
        # list ว่าง
        if not numbers:
            # return list ว่าง
            return None

        # กำหนดค่าเริ่มต้น
        max_index = 0
        # วนลูปหาค่าmaxใน list
        for i in range(1, len(numbers)):
            if numbers[i] > numbers[max_index]:
                max_index = i
        # return ค่ามากที่สุดที่เจอ
        return max_index

