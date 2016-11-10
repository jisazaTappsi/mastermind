#!/usr/bin/env python

"""Test for code.py"""

import unittest

from boolean_solver.code import Code
from tests.generated_code import code_functions as f
from boolean_solver.conditions import Conditions
from tests.testing_helpers import common_testing_code


__author__ = 'juan pablo isaza'


class CodeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        common_testing_code.reset_functions_file(f.__file__, hard_reset=True)

    def test_comparison_operators(self):

        i = Code()
        j = Code()
        self.assertTrue(isinstance(i == 2, Code))
        self.assertTrue(isinstance(2 == i, Code))
        self.assertTrue(isinstance(i == j, Code))
        self.assertTrue(isinstance(i != 2, Code))
        self.assertTrue(isinstance(2 != i, Code))
        self.assertTrue(isinstance(i != j, Code))
        self.assertTrue(isinstance(i < 2, Code))
        self.assertTrue(isinstance(2 < i, Code))
        self.assertTrue(isinstance(i < j, Code))
        self.assertTrue(isinstance(i > 2, Code))
        self.assertTrue(isinstance(2 > i, Code))
        self.assertTrue(isinstance(i > j, Code))
        self.assertTrue(isinstance(i <= 2, Code))
        self.assertTrue(isinstance(2 <= i, Code))
        self.assertTrue(isinstance(i <= j, Code))
        self.assertTrue(isinstance(i >= 2, Code))
        self.assertTrue(isinstance(2 >= i, Code))
        self.assertTrue(isinstance(i >= j, Code))

    def test_arithmetic_operators(self):

        i = Code()
        j = Code()
        self.assertTrue(isinstance(i + 2, Code))
        self.assertTrue(isinstance(2 + i, Code))
        self.assertTrue(isinstance(i + j, Code))
        self.assertTrue(isinstance(i - 2, Code))
        self.assertTrue(isinstance(2 - i, Code))
        self.assertTrue(isinstance(i - j, Code))
        self.assertTrue(isinstance(i * 2, Code))
        self.assertTrue(isinstance(2 * i, Code))
        self.assertTrue(isinstance(i * j, Code))
        self.assertTrue(isinstance(i / 2, Code))
        self.assertTrue(isinstance(2 / i, Code))
        self.assertTrue(isinstance(i / j, Code))
        self.assertTrue(isinstance(i % 2, Code))
        self.assertTrue(isinstance(2 % i, Code))
        self.assertTrue(isinstance(i % j, Code))
        self.assertTrue(isinstance(i ** 2, Code))
        self.assertTrue(isinstance(2 ** i, Code))
        self.assertTrue(isinstance(i ** j, Code))
        self.assertTrue(isinstance(i // 2, Code))
        self.assertTrue(isinstance(2 // i, Code))
        self.assertTrue(isinstance(i // j, Code))


    # TODO: NOT READY TO IMPLEMENT THESE. NOT SURE ABOUT CONSEQUENCES!
    """
    def test_logical_operators(self):

        i = Code()
        j = Code()
        self.assertTrue(isinstance(i and 2, Code))
        self.assertTrue(isinstance(2 and i, Code))
        self.assertTrue(isinstance(i and j, Code))
        self.assertTrue(isinstance(i or 2, Code))
        self.assertTrue(isinstance(2 or i, Code))
        self.assertTrue(isinstance(i or j, Code))
        self.assertTrue(isinstance(i not 2, Code))
        self.assertTrue(isinstance(2 not i, Code))
        self.assertTrue(isinstance(i not j, Code))
    """

    # TODO: missing the real part of composition!.
    def test_composition(self):
        """
        Complex expression is assembled, should print out the same value.
        """

        i = Code()
        j = Code()
        k = Code()
        l = Code()

        c = j + i ** i // 5 / l < j - k
        c.add_locals(locals())
        self.assertEqual(str(c), 'j + i ** i // 5 / l < j - k')

    def test_code_with_int(self):
        """
        When user declares
        >>> v = Code()
        and
        >>> code_object = v == 2
        Then code_object should be of type Code, rather than boolean and
        >>>str(code_object)
        'v == 2'
        """

        v = Code()
        code_object = v == 2
        code_object.add_locals(locals())

        self.assertTrue(isinstance(code_object, Code))
        self.assertEqual(str(code_object), 'v == 2')

    def test_code_with_code(self):
        """
        When user declares
        >>> v = Code()
        >>> w = Code()
        and
        >>> code_object = v == w
        Then code_object should be of type Code, rather than boolean and
        >>>str(code_object)
        'v == w'
        """

        v = Code()
        w = Code()
        code_object = v == w
        code_object.add_locals(locals())

        self.assertTrue(isinstance(code_object, Code))
        self.assertEqual(str(code_object), 'v == w')

    def test_factoring_with_code_var(self):
        """This is a hard test from test_code_generator.py, but additionally here it is added Code instances :)"""
        function = f.factor_code_with_code
        output_code = 'i * 2'
        code1_str = 'i == 9'
        code2_str = 'i == 7'

        code = ['def ' + function.__name__ + '(i):',
                '',
                '    if ' + code1_str + ' or ' + code2_str + ':',
                '        return ' + output_code,
                '',
                '    return False']

        i = Code()
        cond = Conditions(i == 9, output=i*2)
        cond.add(i == 7, output=i*2)
        solution = cond.solve(self, function, local_vars=locals())

        self.assertEqual(solution.implementation, code)

    def test_factor_ordered_with_code(self):
        """This is a hard test from test_code_generator.py, but additionally here it is added Code vars :)"""

        function = f.factor_ordered_with_code
        right_str = 'i * j'
        code1_str = 'i != 0'
        code2_str = 'i < 1'
        code3_str = 'i > j'

        code = ['def ' + function.__name__ + '(i, j):',
                '',
                '    if {0} and {1} or {2}:'.format(code1_str, code2_str, code3_str),
                '        return ' + right_str,
                '',
                '    return False']

        i = Code()
        j = Code()
        cond = Conditions(i != 0,
                          i < 1,
                          output=i * j)
        cond.add(i > j, output=i * j)
        solution = cond.solve(self, function, local_vars=locals())

        self.assertEqual(solution.implementation, code)

if __name__ == '__main__':
    unittest.main()
