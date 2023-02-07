"""Service class module."""

from typing import Mapping

from ansys.api.platform.instancemanagement.v1.product_instance_manager_pb2 import (
    Service as ServiceV1,
)
import grpc

from ansys.platform.instancemanagement import default_configuration
from ansys.platform.instancemanagement.interceptor import header_adder_interceptor


class Service:
    """Provides an entry point for communicating with a remote product."""

    _uri: str
    _headers: Mapping[str, str]

    @property
    def uri(self) -> str:
        """Uniform resource indicator (URI) to reach the service.

        For gRPC, this is a valid URI following gRPC-name resolution
        syntax. For example, https://grpc.github.io/grpc/core/md_doc_naming.html.

        For HTTP or REST, this is a valid http or https URI. It is the base
        path of the service API.
        """
        return self._uri

    @property
    def headers(self) -> Mapping[str, str]:
        """Headers necessary to communicate with the service.

        For a gRPC service, this should be translated into metadata included in
        every communication with the service.

        For a REST-like service, this should be translated into headers included in
        every communication with the service.
        """
        return self._headers

    def __init__(self, uri: str, headers: Mapping[str, str]):
        """Create a Service."""
        self._uri = uri
        self._headers = headers

    def __eq__(self, obj):
        """Test for equality."""
        return isinstance(obj, Service) and obj.headers == self.headers and obj.uri == self.uri

    def __repr__(self):
        """Python callable representation."""
        return f"Service(uri={repr(self.uri)}, headers={repr(self.headers)})"

    def _build_grpc_channel(
        self,
        **kwargs,
    ) -> grpc.Channel:
        """Build a gRPC channel communicating with the product instance.

        Parameters
        -----------
        kwargs: list, optional
            Named arguments for gRPC construction.
            They are passed to ``grpc.insecure_channel``.

        Returns
        -------
        grpc.Channel
            gRPC channel ready to be used for communicating with the service.
        """
        headers = self.headers.items()
        interceptor = header_adder_interceptor(headers)
        potential_port_number = self.uri.split(":")[-1]
        is_secure_port = potential_port_number.isdecimal() and int(potential_port_number) == 443
        if is_secure_port:
            configuration = default_configuration()
            credentials = grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(),
                grpc.access_token_call_credentials(configuration.access_token),
            )
            channel = grpc.secure_channel(self.uri, credentials, **kwargs)
        else:
            channel = grpc.insecure_channel(self.uri, **kwargs)
        return grpc.intercept_channel(channel, interceptor)

    @staticmethod
    def _from_pim_v1(service: ServiceV1):
        """Build a definition from the PIM API v1 protobuf object.

        Parameters
        ----------
        service : ServiceV1
            Raw PIM API v1 protobuf object.

        Returns
        -------
        Service
            The PyPIM service
            PyPIM service definition.
        """
        return Service(uri=service.uri, headers=service.headers)
