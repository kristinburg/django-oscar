from decimal import Decimal as D

from django.test import TestCase
from django_dynamic_fixture import G

from oscar.apps.offer import models
from oscar.apps.basket.models import Basket
from oscar.test.basket import add_product, add_products


class TestAMultibuyDiscountAppliedWithCountCondition(TestCase):

    def setUp(self):
        range = models.Range.objects.create(
            name="All products", includes_all_products=True)
        self.condition = models.CountCondition.objects.create(
            range=range,
            type=models.Condition.COUNT,
            value=3)
        self.benefit = models.MultibuyDiscountBenefit.objects.create(
            range=range,
            type=models.Benefit.MULTIBUY,
            value=1)
        self.basket = G(Basket)

    def test_applies_correctly_to_empty_basket(self):
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('0.00'), result.discount)
        self.assertEqual(0, self.basket.num_items_with_discount)
        self.assertEqual(0, self.basket.num_items_without_discount)

    def test_applies_correctly_to_basket_which_matches_condition(self):
        add_product(self.basket, D('12.00'), 3)
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('12.00'), result.discount)
        self.assertEqual(3, self.basket.num_items_with_discount)
        self.assertEqual(0, self.basket.num_items_without_discount)

    def test_applies_correctly_to_basket_which_exceeds_condition(self):
        add_products(self.basket, [
            (D('4.00'), 4), (D('2.00'), 4)])
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('2.00'), result.discount)
        self.assertEqual(3, self.basket.num_items_with_discount)
        self.assertEqual(5, self.basket.num_items_without_discount)


class TestAMultibuyDiscountAppliedWithAValueCondition(TestCase):

    def setUp(self):
        range = models.Range.objects.create(
            name="All products", includes_all_products=True)
        self.condition = models.ValueCondition.objects.create(
            range=range,
            type=models.Condition.VALUE,
            value=D('10.00'))
        self.benefit = models.MultibuyDiscountBenefit.objects.create(
            range=range,
            type=models.Benefit.MULTIBUY,
            value=1)
        self.basket = G(Basket)

    def test_applies_correctly_to_empty_basket(self):
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('0.00'), result.discount)
        self.assertEqual(0, self.basket.num_items_with_discount)
        self.assertEqual(0, self.basket.num_items_without_discount)

    def test_applies_correctly_to_basket_which_matches_condition(self):
        add_product(self.basket, D('5.00'), 2)
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('5.00'), result.discount)
        self.assertEqual(2, self.basket.num_items_with_discount)
        self.assertEqual(0, self.basket.num_items_without_discount)

    def test_applies_correctly_to_basket_which_exceeds_condition(self):
        add_products(self.basket, [(D('4.00'), 2), (D('2.00'), 2)])
        result = self.benefit.apply(self.basket, self.condition)
        self.assertEqual(D('2.00'), result.discount)
        self.assertEqual(3, self.basket.num_items_with_discount)
        self.assertEqual(1, self.basket.num_items_without_discount)
