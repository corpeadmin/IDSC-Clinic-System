"""Deploy an exact tested commit and wait for Render to report that commit live."""

import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class ReleaseError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def render_request(path, key, payload=None):
    request = Request("https://api.render.com/v1/" + path,
                      data=None if payload is None else json.dumps(payload).encode(),
                      headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json"},
                      method="GET" if payload is None else "POST")
    try:
        with build_opener(NoRedirect).open(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError, OSError, ValueError):
        raise ReleaseError("Render API request failed; check the private service settings and dashboard.") from None


def deploy(service_id, key, revision, repository, *, request=render_request, sleep=time.sleep, now=time.monotonic):
    if not re.fullmatch(r"srv-[a-z0-9]+", service_id) or not key or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ReleaseError("Set a service ID, private API key and full tested commit SHA.")
    base = "services/" + service_id
    service = request(base, key)
    if service.get("repo", "").removesuffix(".git").rstrip("/") != "https://github.com/" + repository or service.get("branch") != "main":
        raise ReleaseError("Render service must target the expected repository and main branch.")
    # Independently triggered builds would bypass the CI dependency gate.
    if service.get("autoDeploy") != "no":
        raise ReleaseError("Disable Render auto-deploy before enabling the CI release job.")
    release = request(base + "/deploys", key, {"commitId": revision, "clearCache": "do_not_clear"})
    release_id = release.get("id", "")
    if not re.fullmatch(r"dep-[a-z0-9]+", release_id):
        raise ReleaseError("Render did not return a deployment identifier.")
    deadline = now() + 900
    while now() < deadline:
        release = request(base + "/deploys/" + release_id, key)
        state = release.get("status")
        if state == "live":
            if release.get("commit", {}).get("id") != revision:
                raise ReleaseError("The live backend revision does not match the tested commit.")
            print("Render reports the tested backend commit live.")
            return
        if state in {"build_failed", "update_failed", "pre_deploy_failed", "canceled", "deactivated"}:
            raise ReleaseError("Render deployment failed; inspect the service dashboard.")
        sleep(10)
    raise ReleaseError("Timed out waiting for Render; inspect the deployment before retrying.")


if __name__ == "__main__":
    try:
        deploy(os.environ["RENDER_SERVICE_ID"], os.environ["RENDER_API_KEY"],
               os.environ["GITHUB_SHA"], os.environ["GITHUB_REPOSITORY"])
    except (KeyError, ReleaseError) as exc:
        raise SystemExit(str(exc)) from None
