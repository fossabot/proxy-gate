from app.config import ProxyGateConfig, ConfigHandler


class TestProxyGate:
    def test_proxy_gate_defaults(self):
        proxy_gate = ProxyGateConfig()
        assert proxy_gate("allowed_auth_methods") == ["google", "plex"]
        assert proxy_gate("app_name") == "Proxy Gate"
        assert proxy_gate(
            "secret_key_validity"
        ) == ConfigHandler.time_duration_to_seconds("3d")
        assert proxy_gate(
            "secret_key_interim_validity"
        ) == ConfigHandler.time_duration_to_seconds("7d")

    def test_same_class(self):
        proxy_gate1 = ProxyGateConfig()
        proxy_gate2 = ProxyGateConfig()
        assert proxy_gate1 is proxy_gate2
