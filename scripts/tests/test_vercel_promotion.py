import unittest

from scripts.promote_vercel import promote, PromotionError


class VercelPromotionTests(unittest.TestCase):
    def provider(self, *, project=None, deployment=None, confirmed=True, fail_post=False):
        calls = []

        def request(path, key, method="GET"):
            calls.append((path, method))
            if method == "POST":
                if fail_post:
                    raise PromotionError("Uncertain provider response")
                return {}
            if path.startswith("v2/"):
                published = confirmed and any(m == "POST" for _, m in calls)
                return {"aliases": [{"alias": "clinic.vercel.app"}]} if published else {"aliases": []}
            if path.startswith("v13/"):
                return {"id": "dpl_test", "projectId": "prj_test", "target": "production",
                        "readyState": "READY", "url": "clinic-test.vercel.app", **(deployment or {})}
            return {"id": "prj_test", "accountId": "team_test", **(project or {})}
        return request, calls

    def run_promotion(self, provider, **kwargs):
        return promote("prj_test", "team_test", "dpl_test", "https://clinic-test.vercel.app",
                       "synthetic-token", "https://clinic.vercel.app", request=provider, **kwargs)

    def test_promotes_checked_deployment_and_confirms_exact_production_target(self):
        provider, calls = self.provider()
        self.run_promotion(provider)
        self.assertEqual(calls, [("v9/projects/prj_test?teamId=team_test", "GET"),
                                 ("v13/deployments/dpl_test?teamId=team_test", "GET"),
                                 ("v10/projects/prj_test/promote/dpl_test?teamId=team_test", "POST"),
                                 ("v2/deployments/dpl_test/aliases?teamId=team_test", "GET")])

    def test_wrong_owner_or_project_cannot_trigger_promotion(self):
        for project in [{"id": "prj_other"}, {"accountId": "team_other"}]:
            provider, calls = self.provider(project=project)
            with self.assertRaises(PromotionError):
                self.run_promotion(provider)
            self.assertEqual(len(calls), 1)

    def test_rejects_preview_unready_wrong_project_and_unchecked_url_before_mutation(self):
        for change in [{"target": "preview"}, {"readyState": "BUILDING"}, {"projectId": "prj_other"},
                       {"id": "dpl_other"}, {"url": "unchecked.vercel.app"}]:
            provider, calls = self.provider(deployment=change)
            with self.subTest(change=change), self.assertRaises(PromotionError):
                self.run_promotion(provider)
            self.assertFalse(any(method == "POST" for _, method in calls))

    def test_bad_ids_and_credential_bearing_urls_do_not_contact_provider(self):
        def unexpected(*args):
            self.fail("Invalid input contacted the provider")
        for deployment_id, url in [("dpl_test/other", "https://clinic-test.vercel.app"),
                                    ("dpl_test", "https://user:private@clinic-test.vercel.app"),
                                    ("dpl_test", "https://clinic-test.vercel.app?private=token"),
                                    ("dpl_test", "https://clinic-test.vercel.app/path")]:
            with self.assertRaises(PromotionError):
                promote("prj_test", "team_test", deployment_id, url, "synthetic-token", "https://clinic.vercel.app", request=unexpected)

    def test_unconfirmed_promotion_does_not_report_success_or_repeat_mutation(self):
        provider, calls = self.provider(confirmed=False)
        clock = iter([0, 0, 200])
        with self.assertRaises(PromotionError):
            self.run_promotion(provider, sleep=lambda _: None, now=lambda: next(clock))
        self.assertEqual(sum(method == "POST" for _, method in calls), 1)

    def test_uncertain_mutation_is_not_retried(self):
        provider, calls = self.provider(fail_post=True)
        with self.assertRaises(PromotionError):
            self.run_promotion(provider)
        self.assertEqual(sum(method == "POST" for _, method in calls), 1)
