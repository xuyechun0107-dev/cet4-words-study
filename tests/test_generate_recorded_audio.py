import io
import json
import sys
import types
import unittest
from urllib.error import HTTPError
from unittest.mock import patch


# The API client has no audio-runtime dependency. Stub those optional build
# packages so this focused unit test can run without downloading the TTS model.
sys.modules.setdefault("lameenc", types.ModuleType("lameenc"))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
kokoro_onnx = types.ModuleType("kokoro_onnx")
kokoro_onnx.Kokoro = object
sys.modules.setdefault("kokoro_onnx", kokoro_onnx)

import generate_recorded_audio as audio


class PresenceAwareApiClientTests(unittest.TestCase):
    @staticmethod
    def response(payload):
        return io.BytesIO(json.dumps(payload).encode("utf-8"))

    def test_joins_on_401_and_renews_an_expired_lease(self):
        requests = []
        actions = iter(
            [
                401,
                {"admitted": True, "token": "token-one", "lease_seconds": 90},
                [{"slug": "book"}],
                401,
                {"admitted": True, "token": "token-two", "lease_seconds": 90},
                [],
            ]
        )

        def open_request(request, timeout):
            self.assertEqual(timeout, 120)
            requests.append(request)
            action = next(actions)
            if action == 401:
                raise HTTPError(
                    request.full_url,
                    401,
                    "Unauthorized",
                    hdrs=None,
                    fp=self.response({"detail": "presence required"}),
                )
            return self.response(action)

        client = audio.PresenceAwareApiClient("https://api.example.test/")
        with patch.object(audio.urllib.request, "urlopen", side_effect=open_request):
            self.assertEqual(client.fetch("/v1/wordbooks"), [{"slug": "book"}])
            self.assertEqual(client.fetch("/v1/sentences?offset=0&limit=200"), [])

        self.assertEqual(len(requests), 6)
        first_join = requests[1]
        renewed_join = requests[4]
        self.assertEqual(first_join.get_method(), "POST")
        self.assertEqual(json.loads(first_join.data), {"token": None})
        self.assertEqual(json.loads(renewed_join.data), {"token": "token-one"})
        self.assertEqual(
            dict(requests[2].header_items())["X-presence-token"], "token-one"
        )
        self.assertEqual(
            dict(requests[5].header_items())["X-presence-token"], "token-two"
        )

    def test_unprotected_api_keeps_the_original_single_get_behavior(self):
        requests = []

        def open_request(request, timeout):
            requests.append(request)
            return self.response([])

        client = audio.PresenceAwareApiClient("https://api.example.test")
        with patch.object(audio.urllib.request, "urlopen", side_effect=open_request):
            self.assertEqual(client.fetch("/v1/wordbooks"), [])

        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].get_method(), "GET")
        self.assertNotIn(
            "X-presence-token", dict(requests[0].header_items())
        )


if __name__ == "__main__":
    unittest.main()
