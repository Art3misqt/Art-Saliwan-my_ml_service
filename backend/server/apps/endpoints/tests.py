from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.ml.registry import MLRegistry
from apps.ml.income_classifier.random_forest import RandomForestClassifier
from apps.endpoints.models import Endpoint, MLAlgorithm, MLAlgorithmStatus
from server.wsgi import registry

class EndpointTests(TestCase):
    def test_predict_view(self):
        # setup data
        endpoint_name = "income_classifier"
        algorithm_object = RandomForestClassifier()
        algorithm_name = "random forest"
        algorithm_status = "production"
        algorithm_version = "0.0.1"
        algorithm_owner = "Piotr"
        algorithm_description = "Random Forest with simple pre- and post-processing"
        algorithm_code = "inspect.getsource(RandomForestClassifier)"

        # create endpoint
        endpoint = Endpoint.objects.create(name=endpoint_name, owner=algorithm_owner)
        # create algorithm
        database_object = MLAlgorithm.objects.create(
            name=algorithm_name,
            description=algorithm_description,
            code=algorithm_code,
            version=algorithm_version,
            owner=algorithm_owner,
            parent_endpoint=endpoint
        )
        # create status
        MLAlgorithmStatus.objects.create(
            status=algorithm_status,
            created_by=algorithm_owner,
            parent_mlalgorithm=database_object,
            active=True
        )
        # add to registry
        registry.endpoints[database_object.id] = algorithm_object

        client = APIClient()
        input_data = {
            "age": 37,
            "workclass": "Private",
            "fnlwgt": 34146,
            "education": "HS-grad",
            "education-num": 9,
            "marital-status": "Married-civ-spouse",
            "occupation": "Craft-repair",
            "relationship": "Husband",
            "race": "White",
            "sex": "Male",
            "capital-gain": 0,
            "capital-loss": 0,
            "hours-per-week": 68,
            "native-country": "United-States"
        }
        url = reverse("predict", kwargs={"endpoint_name": endpoint_name})
        response = client.post(url, input_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "<=50K")
        self.assertTrue("request_id" in response.data)
        self.assertTrue("status" in response.data)
