from typing import Any

from rest_framework import status
from care.facility.models.ambulance import Ambulance, AmbulanceDriver
from care.utils.tests.test_base import TestBase
from config.tests.helper import mock_equal


class TestAmbulance(TestBase):
    """Test patient APIs"""
    @classmethod
    def setUpClass(cls):
        """
        Runs once per class
            - Initialize the attributes useful for class methods
        """
        super(TestAmbulance, cls).setUpClass()

    def get_base_url(self):
        return "/api/v1/ambulance"

    def test_login_required(self):
        """Test permission error is raised for unauthorised access"""
        # logout the user logged in during setUp function
        self.client.logout()
        response = self.client.post(self.get_url(), {},)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ambulance_list_is_accessible_by_url_location(self):
        """Test user can retreive their ambulance list by the url"""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def get_detail_representation(self, ambulance: Any = None) -> dict:
        return {
            "id": ambulance.id,
            "vehicle_number": ambulance.vehicle_number,
            "owner_name": ambulance.owner_name,
            "owner_phone_number": ambulance.owner_phone_number,
            "owner_is_smart_phone": ambulance.owner_is_smart_phone,
            "primary_district": ambulance.primary_district.name,
            "secondary_district": ambulance.primary_district.name,
            "third_district": ambulance.primary_district.name,
            "has_oxygen": ambulance.has_oxygen,
            "has_ventilator": ambulance.has_ventilator,
            "has_suction_machine": ambulance.has_suction_machine,
            "has_defibrillator": ambulance.has_defibrillator,
            "insurance_valid_till_year": ambulance.insurance_valid_till_year,
            "ambulance_type": ambulance.ambulance_type,
            "price_per_km": ambulance.price_per_km
        }

    def get_ambulance_data(self, district=None, user=None):
        user = user or self.user
        return {
            "drivers": [{"name":"test", "phone_number": "8888888888", "is_smart_phone": True},],
            "vehicle_number": "KL13AB1234",
            "owner_name": "Rahul",
            "owner_phone_number": "8888888888",
            "owner_is_smart_phone": True,
            "primary_district": (district or self.district).id,
            "secondary_district": (district or self.district).id,
            "third_district": (district or self.district).id,
            "has_oxygen": True,
            "has_ventilator": True,
            "has_suction_machine": True,
            "has_defibrillator": True,
            "insurance_valid_till_year": 2020,
            "ambulance_type": 1,
            "price_per_km":7.00
        }

    def test_create_ambulance(self):
        """
        Test users can create ambulance
            - login a normal user
            - verify creation response code is 201
            - verify inserted values
        """
        data = self.get_ambulance_data()
        response = self.client.post(self.get_url()+'create/', data, format="json")
        # test status code

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test response data

        # Facility exists
        ambulance = Ambulance.objects.filter(vehicle_number="KL13AB1234").first()
        self.assertIsNotNone(ambulance)
        self.assertEqual(response.json()["id"], ambulance.id)

    def test_retrieve(self):
        """Test ambulance data is returned as expected"""
        stats_data = self.get_ambulance_data()
        del stats_data['drivers']
        stats_data['vehicle_number'] = "KL13AB1235"
        stats_data['primary_district'] = self.district
        stats_data['secondary_district'] = self.district
        stats_data['third_district'] = self.district
        obj = Ambulance.objects.create(**stats_data)
        response = self.client.get(self.get_url(entry_id=obj.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_ambulance(self):
        """Test ambulance data is deleted as expected"""
        stats_data = self.get_ambulance_data()
        del stats_data['drivers']
        stats_data['vehicle_number'] = "KL13AB1236"
        stats_data['primary_district'] = self.district
        stats_data['secondary_district'] = self.district
        stats_data['third_district'] = self.district
        obj = Ambulance.objects.create(**stats_data)
        count = Ambulance.objects.filter(owner_phone_number="8888888888",).count()
        response = self.client.delete(self.get_url(entry_id=obj.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            Ambulance.objects.filter(owner_phone_number="8888888888",).count(), count - 1,
        )

    def test_create_ambulance_driver(self):
        stats_data = self.get_ambulance_data()
        del stats_data['drivers']
        stats_data['vehicle_number'] = "KL13AB1237"
        stats_data['primary_district'] = self.district
        stats_data['secondary_district'] = self.district
        stats_data['third_district'] = self.district
        obj = Ambulance.objects.create(**stats_data)
        data = {"name":"test1", "phone_number": "7777777777", "is_smart_phone": True}
        response = self.client.post(self.get_url()+'{0}/add_driver'.format(obj.id), data, format="json")
        # test status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_remove_ambulance_driver(self):
        stats_data = self.get_ambulance_data()
        del stats_data['drivers']
        stats_data['vehicle_number'] = "KL13AB1238"
        stats_data['primary_district'] = self.district
        stats_data['secondary_district'] = self.district
        stats_data['third_district'] = self.district
        obj = Ambulance.objects.create(**stats_data)
        data = {"ambulance":obj,"name":"test2", "phone_number": "6666666666", "is_smart_phone": True}
        obj_driver = AmbulanceDriver.objects.create(**data)
        response = self.client.delete(self.get_url()+'{0}/remove_driver'.format(obj.id), format="json")
        # test status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ambulance_list(self):
        """Test ambulance list is displayed with the correct data"""

        data = self.get_ambulance_data()
        data['vehicle_number'] = "KL13AB1211"
        response = self.client.post(self.get_url()+'create/', data, format="json")
        data['vehicle_number'] = "KL13AB1212"
        response = self.client.post(self.get_url()+'create/', data, format="json")
        count = Ambulance.objects.filter(owner_phone_number="8888888888",).count()


        # stats_data = self.get_ambulance_data()
        # del stats_data['drivers']
        # stats_data['vehicle_number'] = "KL13AB1211"
        # stats_data['primary_district'] = self.district
        # stats_data['secondary_district'] = self.district
        # stats_data['third_district'] = self.district
        # obj = Ambulance.objects.create(**stats_data)

        # stats_data = self.get_ambulance_data()
        # del stats_data['drivers']
        # stats_data['vehicle_number'] = "KL13AB1212"
        # stats_data['primary_district'] = self.district
        # stats_data['secondary_district'] = self.district
        # stats_data['third_district'] = self.district
        # obj = Ambulance.objects.create(**stats_data)

        response = self.client.get(self.get_url())
        print("OOOOOOOOOOOOOOOOOOO", count)
        print("OOOOOOOOOOOOOOOOOOO", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)