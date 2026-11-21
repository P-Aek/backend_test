"""
เขียบนโปรแกรมแปลงตัวเลยเป็นตัวเลข roman

[Input]
number: list of numbers

[Output]
roman_text: roman number

[Example 1]
input = 101
output = CI

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    roman_word = {
        "1" : "I",
        "4" : "IV",
        "5" : "V",
        "9" : "IX",
        "10" : "X",
        "40" : "XL",
        "50" : "L",
        "90" : "XC",
        "100" : "C",
        "400" : "CD",
        "500" : "D",
        "900" : "CM",
        "1000" : "M"
    }

    def number_to_roman(self, number: int) -> str:
        # ดักค่าที่ไม่เข้าเงื่อนไข
        if number < 0:
            return "number can not less than 0."
        # เลขโรมันไม่มีเลข 0
        if number < 1:
            return "There is no zero in Roman numerals."
        # list เก็บ roman word ทีละค่า
        roman = []
        # sort key ใน roman_word
        values = sorted(map(int, self.roman_word), reverse=True)

        for value in values:
            while number >= value:
                roman.append(self.roman_word[str(value)]) # นำ value ไปเทียบค่าใน roman_word และเติมใน list roman
                number -= value

        return "".join(roman)

if __name__ == "__main__":
    sol = Solution()
    number = int(input("input: "))
    print(f"output: {sol.number_to_roman(number)}")