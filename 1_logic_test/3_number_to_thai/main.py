"""
เขียบนโปรแกรมแปลงตัวเลยเป็นคำอ่านภาษาไทย

[Input]
number: positive number rang from 0 to 10_000_000

[Output]
num_text: string of thai number call

[Example 1]
input = 101
output = หนึ่งร้อยเอ็ด

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    digit_words = {
        "0" : "ศูนย์",
        "1" : "หนึ่ง",
        "2" : "สอง",
        "3" : "สาม",
        "4" : "สี่",
        "5" : "ห้า",
        "6" : "หก",
        "7" : "เจ็ด",
        "8" : "แปด",
        "9" : "เก้า"
    }

    place_words = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน", "สิบล้าน"]
 
    def number_to_thai(self, number: int) -> str:
        # ดักค่าที่ไม่ใช่
        if number < 0:
            return "number can not less than 0"
        if number > 10_000_000:
            return "positive number rang from 0 to 10_000_000"

        # คืนค่าเลข 0 = ศูนย์
        if number == 0:
            return self.digit_words["0"]

        digits = str(number) # แปลงค่า number จาก int -> str
        words = [] # list เก็บค่า

        # วนลูปใน digits output ค่า (i,digit)
        for i, digit in enumerate(digits):
            place_index = len(digits) - i - 1 # หาตำแหน่งของ index -> เช่น 123: place_index ของ 1 = 3 - 0 - 1 = 2 -> เลข 1 อยู่ใน place_words[2] = "ร้อย" 

            if digit == "0":
                continue # ถ้าเจอ 0 ให้ไปต่อ
            # เงื่อนไข
            if place_index == 1 and digit == "1":
                words.append("สิบ")
            elif place_index == 1 and digit == "2":
                words.append("ยี่สิบ")
            elif place_index == 0 and digit == "1" and len(digits) > 1:
                words.append("เอ็ด")
            else:
                words.append(self.digit_words[digit] + self.place_words[place_index])

        return "".join(words)


sol = Solution()
number = int(input("input: "))
print(f"Output: {sol.number_to_thai(number)}")