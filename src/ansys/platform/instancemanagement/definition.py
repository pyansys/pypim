"""Definition class module."""

from dataclasses import dataclass, field
from typing import Sequence

from ansys.api.platform.instancemanagement.v1.product_instance_manager_pb2 import (
    Definition as DefinitionV1,
)
from ansys.api.platform.instancemanagement.v1.product_instance_manager_pb2_grpc import (
    ProductInstanceManagerStub,
)

from ansys.platform.instancemanagement.instance import Instance


@dataclass(frozen=True)
class Definition:
    """Provides a definition of a product that can be started using the PIM API.

    The definition is a static object describing a product that can be started remotely.
    """

    name: str
    """Name of the definition.

    This name is chosen by the server and always start with `definitions/`.
    This name is arbitrary. You should not rely on any static value.
    """

    product_name: str
    """Name of the product.

    This is the name of the product that can be started (for example, ``"mapdl"`` or ``"fluent"``).
    """

    product_version: str
    """Version of the product.

    This is a string describing the version.
    When the product is following the Ansys unified installation release process,
    it will be the three-number version, such as "221".
    """

    available_service_names: Sequence[str]
    """List of the available service names.

    If the product exposes a gRPC API, the service will be named "grpc".
    If the product exposes a REST-like API, the service will be named "http".
    Custom entries might also be listed, either for sidecar services or
    other protocols.
    """

    _stub: ProductInstanceManagerStub = field(default=None, compare=False)

    def create_instance(self, timeout: float = None) -> Instance:
        """Create a product instance from this definition.

        Parameters
        ----------
        timeout : float
            Time in seconds to create the instance. The default is ``None``.

        Returns
        -------
        instance
            Product instance.
        """
        return Instance._create(definition_name=self.name, stub=self._stub, timeout=timeout)

    @staticmethod
    def _from_pim_v1(definition: DefinitionV1, stub: ProductInstanceManagerStub = None):
        """Build a definition from the PIM API v1 protobuf object.

        Parameters
        ----------
        definition : DefinitionV1
            Raw PIM API v1 protobuf object.

        Returns
        -------
        instance
            PyPIM instance definition.

        Raises
        ------
        ValueError: The raw protobuf message is not valid.
        """
        if not definition.name or not definition.name.startswith("definitions/"):
            raise ValueError("A definition name must have a name that starts with ``definitions/``.")

        if not definition.product_name:
            raise ValueError("A definition must have a product name.")

        if not definition.product_version:
            raise ValueError("A definition must have a product version.")

        if not definition.available_service_names or len(definition.available_service_names) == 0:
            raise ValueError("A definition must have at least one service name.")

        return Definition(
            definition.name,
            definition.product_name,
            definition.product_version,
            definition.available_service_names,
            stub,
        )
