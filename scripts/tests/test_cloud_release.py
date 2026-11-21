import json
import tempfile
import unittest
from pathlib import Path

from scripts.deploy_render import ReleaseError, deploy
from scripts.prepare_cloud_frontend import https_origin, prepare


SHA = "a" * 40
REPO = "corpeadmin/IDSC-Clinic-System"


class RenderReleaseTests(unittest.TestCase):
    def provider(self, **overrides):
        calls = []
        service = {"repo": "https://github.com/" + REPO, "branch": "main", "autoDeploy": "no"}
        service.update(overrides)

        def request(path, key, payload=None):
            calls.append((path, payload))
            if path.endswith("/deploys"):
                return {"id": "dep-synthetic123"}
            if "/deploys/" in path:
                return {"status": "live", "commit": {"id": SHA}}
            return service
        return request, calls

    def test_deploys_only_exact_tested_commit_to_expected_service(self):
        provider, calls = self.provider()
        deploy("srv-synthetic123", "synthetic-key", SHA, REPO, request=provider)
        self.assertEqual(calls[1], ("services/srv-synthetic123/deploys", {"commitId": SHA, "clearCache": "do_not_clear"}))
        self.assertEqual(len(calls), 3)

    def test_wrong_repository_branch_or_independent_autodeploy_stops_before_release(self):
        for override in [{"repo": "https://github.com/other/repository"}, {"branch": "other"}, {"autoDeploy": "yes"}]:
            with self.subTest(override=override):
                provider, calls = self.provider(**override)
                with self.assertRaises(ReleaseError):
                    deploy("srv-synthetic123", "synthetic-key", SHA, REPO, request=provider)
                self.assertEqual(len(calls), 1)

    def test_live_revision_must_match_tested_commit(self):
        provider, calls = self.provider()

        def wrong_revision(path, key, payload=None):
            result = provider(path, key, payload)
            if "/deploys/" in path:
                result["commit"]["id"] = "b" * 40
            return result
        with self.assertRaisesRegex(ReleaseError, "does not match"):
            deploy("srv-synthetic123", "synthetic-key", SHA, REPO, request=wrong_revision)

    def test_missing_configuration_does_not_contact_host(self):
        def unexpected(*args):
            self.fail("Invalid deployment input contacted the host")
        with self.assertRaises(ReleaseError):
            deploy("srv-synthetic123", "", SHA, REPO, request=unexpected)

    def test_failed_and_uncertain_deployments_do_not_report_success_or_retry_creation(self):
        for state in ["build_failed", "update_failed", "pre_deploy_failed", "canceled", "building"]:
            with self.subTest(state=state):
                provider, calls = self.provider()

                def status(path, key, payload=None):
                    result = provider(path, key, payload)
                    if "/deploys/" in path:
                        result["status"] = state
                    return result
                clock = iter([0, 0, 1000])
                with self.assertRaises(ReleaseError):
                    deploy("srv-synthetic123", "synthetic-key", SHA, REPO,
                           request=status, now=lambda: next(clock), sleep=lambda _: None)
                self.assertEqual(sum(path.endswith('/deploys') for path, _ in calls), 1)


class CloudPackagingTests(unittest.TestCase):
    def test_backend_requires_https_origin_without_embedded_credentials(self):
        for value in ["http://api.example.test", "https://user:key@api.example.test", "https://api.example.test/api", "https://api.example.test?token=private", "https://localhost"]:
            with self.subTest(origin=value), self.assertRaises(ValueError):
                https_origin(value)

    def test_packages_only_built_files_and_routes_api_before_spa(self):
        import re

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'frontend/dist'
            source.mkdir(parents=True)
            (source / 'index.html').write_text('<html>IDSC Clinic</html>')
            (root / '.env').write_text('PRIVATE=must-not-upload')
            output = prepare(root, 'https://api.example.test')
            self.assertEqual(list((output / 'static').iterdir()), [output / 'static/index.html'])
            config = json.loads((output / 'config.json').read_text())
            route = config['routes'][0]
            for path in ['/api/auth/login/', '/api/does-not-exist', '/docs', '/docs/', '/health', '/admin/', '/static/admin/css/base.css']:
                match = re.fullmatch(route['src'], path)
                self.assertIsNotNone(match, path)
                self.assertEqual(route['dest'].replace('$1', match[1]), 'https://api.example.test' + path)
            self.assertIsNone(re.fullmatch(route['src'], '/students'))
            self.assertEqual(config['routes'][1], {'handle': 'filesystem'})
            self.assertEqual(config['routes'][-1]['dest'], '/index.html')
            self.assertEqual(route['headers']['Cache-Control'], 'no-store')

    def test_missing_frontend_build_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            prepare(folder, 'https://api.example.test')


if __name__ == '__main__':
    unittest.main()
