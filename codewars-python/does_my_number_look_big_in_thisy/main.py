# A Narcissistic Number (or Armstrong Number) is a positive number which is the sum of its own digits, each raised to the power of the number of digits in a given base. In this Kata, we will restrict ourselves to decimal (base 10).
# 
# For example, take 153 (3 digits), which is narcissistic:
# 
#     1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153
# and 1652 (4 digits), which isn't:
# 
#     1^4 + 6^4 + 5^4 + 2^4 = 1 + 1296 + 625 + 16 = 1938
#
# The Challenge:
# 
# Your code must return true or false (not 'true' and 'false') depending upon whether the given number is a Narcissistic number in base 10.


def narcissistic(number_to_check: int) -> bool:

    digits = []
    initial_number = number_to_check
    while number_to_check != 0:
        digits.append(number_to_check % 10)
        number_to_check = number_to_check // 10
        
    number_length = len(digits)
    return sum(x ** number_length for x in digits) == initial_number



