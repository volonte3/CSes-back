from django.test import TestCase
from User.models import Entity,Department, User
from Asset.models import AssetClass, Asset, PendingRequests
class AssetTests(TestCase):
    def setUp(self):
        pass
    def test_assert_test(self):
        self.assertEqual(1, 1)
# Create your tests here.
