"""
เขียนโปรแกรมหาจำนวนเลข 0 ที่ออยู่ติดกันหลังสุดของค่า factorial โดยห้ามใช้ function from math

[Input]
number: as an integer

[Output]
count: count of tailing zero as an integer

[Example 1]
input = 7
output = 1

[Example 2]
input = -10
output = number can not be negative
"""


class Solution:
    def find_tailing_zeroes(self, number: int) -> int | str:
        # เช็ค number เป็นค่า negative
        if number < 0:
            # คืนค่าเป็น "number can not be negative"
            return "number can not be negative"
        # คำนวณ factorial
        fac = 1 # กำหนดค่า fac เริ่มต้น = 1
        for i in range(1, number+1):
            fac *= i
        # นับเลข 0 ติดกันหลังสุด
        count = 0
        while fac % 10 == 0: # เงื่อนไขลูป ตรวจหาตัวเลขหลักสุดท้ายลงท้ายด้วย 0 ไหม
            count += 1 
            fac //= 10 # หารตัดเศษออก
        return count # คืนค่าที่นับออกมา

if __name__ == "__main__":
    sol = Solution()
    # example
    number = int(input("input = "))
    result = sol.find_tailing_zeroes(number)
    print(f"output = {result}")