"""Promote only the checked production deployment, without account-profile access."""

import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class PromotionError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def vercel_request(path, key, method="GET"):
    req = Request("https://api.vercel.com/" + path, method=method,
                  headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    try:
        with build_opener(NoRedirect).open(req, timeout=30) as response:
            body = response.read(2_000_000)
            return json.loads(body) if body else {}
    except (HTTPError, URLError, OSError, ValueError):
        # Never print provider bodies, headers, private tokens or reset links.
        raise PromotionError("Vercel promotion API failed; inspect project access and deployment status.") from None


def promote(project_id, team_id, deployment_id, staged_origin, key, public_origin, *,
            request=vercel_request, sleep=time.sleep, now=time.monotonic):
    for value, prefix in [(project_id, "prj_"), (team_id, "team_"), (deployment_id, "dpl_")]:
        if not re.fullmatch(re.escape(prefix) + r"[A-Za-z0-9]+", value):
            raise PromotionError("Set the exact Vercel project, team and staged deployment IDs.")
    origin = urlsplit(staged_origin)
    if (not key or origin.scheme != "https" or not origin.hostname
            or not origin.hostname.endswith(".vercel.app") or origin.port
            or origin.username or origin.password or origin.path or origin.query or origin.fragment):
        raise PromotionError("Set a private token and the checked HTTPS Vercel deployment origin.")
    public = urlsplit(public_origin)
    if (public.scheme != "https" or not public.hostname or public.port
            or public.username or public.password or public.path or public.query or public.fragment):
        raise PromotionError("Set the exact stable public HTTPS origin.")
    query = "?" + urlencode({"teamId": team_id})
    project_path = "v9/projects/" + project_id + query
    project = request(project_path, key)
    if project.get("id") != project_id or project.get("accountId") != team_id:
        raise PromotionError("Vercel project ownership does not match the configured target.")
    deployment = request("v13/deployments/" + deployment_id + query, key)
    if (deployment.get("id") != deployment_id or deployment.get("projectId") != project_id
            or deployment.get("target") != "production" or deployment.get("readyState") != "READY"
            or deployment.get("url") != origin.hostname):
        raise PromotionError("Only the checked READY production deployment of this project can be promoted.")
    # A single mutation: an uncertain response must be inspected, never blindly retried.
    request("v10/projects/" + project_id + "/promote/" + deployment_id + query, key, "POST")
    deadline = now() + 180
    while now() < deadline:
        aliases = request("v2/deployments/" + deployment_id + "/aliases" + query, key)
        if any(alias.get("alias") == public.hostname and not alias.get("redirect")
               for alias in aliases.get("aliases", [])):
            print("Vercel confirms the stable public domain points to the checked deployment.")
            return
        sleep(5)
    raise PromotionError("Promotion is not confirmed; inspect Vercel before retrying.")


if __name__ == "__main__":
    try:
        promote(os.environ["VERCEL_PROJECT_ID"], os.environ["VERCEL_ORG_ID"],
                os.environ["STAGED_DEPLOYMENT_ID"], os.environ["STAGED_ORIGIN"], os.environ["VERCEL_TOKEN"],
                os.environ["CLINIC_PUBLIC_ORIGIN"])
    except (KeyError, PromotionError, ValueError) as exc:
        raise SystemExit(str(exc)) from None
