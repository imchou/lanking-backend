import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import UserAccount, Landlord, Rating, Property
from .serializers import UserSerializer, LandlordSerializer, RatingSerializer, PropertySerializer


class BaseUserTest(APITestCase):
	client = APIClient()
	@staticmethod
	def create_user(username="", password="", realnameVisible=""):
		if all([username!="", password!="", realnameVisible!=""]):
			UserAccount.objects.create(username=username, password=password, 
				realnameVisible=False, is_staff=False)

	def setUp(self):
		self.create_user("user1", "password1", False)
		self.create_user("user2", "password2", False)
		self.create_user("user3", "password3", False)
		self.create_user("user4", "password4", False)


class BaseLandlordTest(APITestCase):
	client = APIClient()
	@staticmethod
	def create_landlord(first="", last=""):
		if first != "" and last != "":
			Landlord.objects.create(first=first, last=last, 
				avg_rating=None, sum_rating=0, num_rating=0)

	def setUp(self):
		self.create_landlord("John", "Doe")
		self.create_landlord("Jane", "Doe")
		self.create_landlord("Andrew", "Smith")
		self.create_landlord("Abby", "Smith")
		self.valid_payload = {
			'first': 'Jane',
			'last': 'Smith'
        }
		self.invalid_payload = {
        	'first': '',
        	'last': '',
        }

class CreateLandlordTest(BaseLandlordTest):
	def test_create_valid_landlord(self):
		response = self.client.post(
            reverse('landlords'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
		self.assertEqual(len(Landlord.objects.all()), 5)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_invalid_landlord(self):
		response = self.client.post(
            reverse('landlords'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
		self.assertEqual(len(Landlord.objects.all()), 4)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class QueryLandlordTest(BaseLandlordTest):
	def test_query_landlords_first(self):
		response = self.client.get(
            reverse("landlords") + "?first=jane"
        )
		expected = Landlord.objects.filter(first__icontains="jane")
		serialized = LandlordSerializer(expected, many=True)
		self.assertEqual(response.data, serialized.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_query_landlords_last(self):
		response = self.client.get(
            reverse("landlords") + "?last=doe"
        )
		expected = Landlord.objects.filter(last__icontains="Doe")
		serialized = LandlordSerializer(expected, many=True)
		self.assertEqual(response.data, serialized.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_query_landlords_missing(self):
		response = self.client.get(
            reverse("landlords") + "?last=Johnson"
        )
		self.assertEqual(response.data, [])
		self.assertEqual(response.status_code, status.HTTP_200_OK)

class BaseRatingsTest(APITestCase):
	client = APIClient()
	@staticmethod
	def create_rating(author_id="", landlord_id="", 
		prop_id="", comment="", rating=""):
		if all([author_id!="", landlord_id!="", prop_id!="", comment!="", rating!=""]):
			Rating.objects.create(author_id=author_id, landlord_id=landlord_id, 
									prop_id=prop_id, comment=comment, rating=rating)

	@staticmethod
	def create_landlord(first="", last=""):
		if first != "" and last != "":
			Landlord.objects.create(first=first, last=last, 
				avg_rating=None, sum_rating=0, num_rating=0)

	def setUp(self):
		self.create_landlord("John", "Smith")
		self.create_landlord("Jane", "Doe")
		self.create_rating(1, 12, 1, "Landlord 12's property 1", 3)
		self.create_rating(2, 12, 2, "Landlord 12's property 2", 2)
		self.create_rating(3, 13, 3, "Landlord 13's property 3", 4)
		self.create_rating(4, 13, 4, "Landlord 13's property 4", 5)
		self.valid_payload = {
			'author_id': '5', 
			'landlord_id': '13', 
			'prop_id': '4', 
			'comment': 'Also lived in property 4 from landlord 13, another comment', 
			'rating': '5'
        }
		self.invalid_payload = {
        	'author_id': '', 
			'landlord_id': '', 
			'prop_id': '', 
			'comment': 'This comment should not appear', 
			'rating': ''
        }

class CreateRatingTests(BaseRatingsTest):
	def test_create_valid_rating(self):
		response = self.client.post(
            reverse('ratings'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
		self.assertEqual(Landlord.objects.get(id__exact=12).avg_rating, None)
		self.assertEqual(Landlord.objects.get(id__exact=12).num_rating, 0)
		self.assertEqual(Landlord.objects.get(id__exact=13).avg_rating, 5)
		self.assertEqual(Landlord.objects.get(id__exact=13).num_rating, 1)
		self.assertEqual(len(Rating.objects.all()), 5)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_create_invalid_rating(self):
		response = self.client.post(
            reverse('ratings'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
		self.assertEqual(len(Rating.objects.all()), 4)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)