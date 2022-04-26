from unittest.mock import patch

from ansys.api.platform.instancemanagement.v1 import product_instance_manager_pb2 as pb2
from ansys.api.platform.instancemanagement.v1 import product_instance_manager_pb2_grpc as pb2_grpc

import ansys.platform.instancemanagement as pypim


def test_from_pim_v1_proto():
    definition = pypim.Definition._from_pim_v1(
        pb2.Definition(
            name="definitions/my_def",
            product_name="my_product",
            product_version="221",
            available_service_names=["grpc", "http"],
        )
    )

    assert definition.name == "definitions/my_def"
    assert definition.product_name == "my_product"
    assert definition.product_version == "221"
    assert sorted(definition.available_service_names) == sorted(["grpc", "http"])


def test_create_instance(testing_channel):
    # Arrange
    # A mocked Instance class and a definition
    with patch.object(
        pypim.Instance,
        "_create",
        return_value=pypim.Instance(
            definition_name="definitions/my_def",
            name="instances/something-123",
            ready=False,
            status_message="loading...",
            services={},
        ),
    ) as mock_instance_create:
        stub = pb2_grpc.ProductInstanceManagerStub(testing_channel)
        definition = pypim.Definition(
            name="definitions/my_def",
            product_name="my_product",
            product_version="221",
            available_service_names=["grpc", "http"],
            _stub=stub,
        )

        # Act
        # Create the instance from the definition
        definition.create_instance(0.1)

    # Assert
    # The mocked Instance class was correctly called
    mock_instance_create.assert_called_once_with(
        definition_name="definitions/my_def", timeout=0.1, stub=stub
    )
