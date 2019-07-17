from django.test import TestCase
from app.calc import add, subtract


class CalcTests(TestCase):

    def test_add_num(self):
        """add number test"""
        self.assertEqual(add(1, 5), 6)

    def test_subtract_num(self):
        """add number test"""
        self.assertEqual(subtract(1, 5), 4)
