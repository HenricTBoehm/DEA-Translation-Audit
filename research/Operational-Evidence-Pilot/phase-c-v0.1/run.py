"""Execute the five bounded controls against native PostgreSQL."""
import argparse
import hashlib
import json
from pathlib import Path
import select
import subprocess
from time import perf_counter_ns

from cluster import ADMIN, ROLES, database

HERE = Path(__file__).resolve().parent
COUNTS = ("criteria", "active", "selection_events", "evaluations", "decisions", "sealed_score")


class Attempt:
    def __init__(self, db, name):
        self.db, self.name = db, name
        self.ops, self.times, self.statements = {}, {}, {}
        ddl = (HERE / "schema.sql").read_text().replace("@NS@", name)
        self.use("setup", ADMIN, ddl)

    def use(self, tag, role, sql, *, error=None, parse=False, record=True):
        data, duration = self.db.query(role, self.name, sql, error, f"{self.name}/{tag}")
        if parse:
            data = json.loads(data)
        self.times[tag] = duration
        if record:
            self.ops[tag] = {"login": role, "result": data}
            self.statements[tag] = sql
        return data

    def privileges(self, tag):
        sql = f"""
        SELECT jsonb_object_agg(role, jsonb_build_object(
          'MayCreateVersion', has_column_privilege(role, 'criteria', 'threshold', 'INSERT')
                              AND has_column_privilege(role, 'criteria', 'version', 'INSERT'),
          'MayModifyCriterion', has_column_privilege(role, 'criteria', 'threshold', 'UPDATE'),
          'MaySelectVersion', has_column_privilege(role, 'active', 'version', 'UPDATE'),
          'MayAdjudicate', has_function_privilege(role, '{self.name}.evaluate(text)', 'EXECUTE'),
          'MayCommit', has_function_privilege(role, '{self.name}.bind_decision(text,text,bigint)', 'EXECUTE')
        )) FROM unnest(ARRAY['writer','selector','adjudicator','committer','observer']) AS r(role);
        """
        return self.use(tag, "observer", sql, parse=True)

    def publish(self):
        self.use("publish", "writer", "INSERT INTO criteria(version,threshold) VALUES ('v1',1);")

    def select(self, tag, version, error=None, timeout=False):
        prefix = "SET lock_timeout='150ms';\n" if timeout else ""
        role = "writer" if tag == "writer_select_denied" else "selector"
        sql = prefix + f"UPDATE active SET version='{version}' WHERE singleton;"
        return self.use(tag, role, sql, error=error)

    def check(self, name):
        return self.use(name, "adjudicator", "SELECT to_jsonb(active) FROM active;", parse=True)

    def evaluate(self, key):
        return self.use(key, "adjudicator", f"SELECT evaluate('{key}');", parse=True)

    def finish(self, tag, token, checked, error=None, role="committer"):
        sql = bind(token, checked)
        return self.use(tag, role, sql, error=error, parse=error is None)

    def locked_commit(self, key, checked):
        """Hold the selector row lock, prove a competing update fails, then commit."""
        cmd, env = self.db.command("committer", f"{self.name}/locked_commit")
        started = perf_counter_ns()
        with subprocess.Popen(cmd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, bufsize=0) as client:
            try:
                client.stdin.write(f"SET search_path TO {self.name},pg_catalog; BEGIN; {bind(key, checked)}\n"
                                   .encode())
                if not select.select([client.stdout], [], [], 5)[0]:
                    raise TimeoutError("committer did not return an uncommitted row")
                pending = json.loads(client.stdout.readline())
                self.times["locked_commit_to_pending"] = (perf_counter_ns() - started) / 1e6
                assert self.use("pending_visible_count", "observer",
                                "SELECT count(*) FROM decisions WHERE token='fresh';") == "0"
                self.select("competing_select_while_locked", "v0", error="55P03", timeout=True)
                started = perf_counter_ns()
                tail, err = client.communicate(input=b"COMMIT;\n", timeout=5)
                self.times["locked_commit_release"] = (perf_counter_ns() - started) / 1e6
                if client.returncode or tail or err:
                    raise AssertionError((client.returncode, tail, err))
            except BaseException:
                client.kill()
                raise
        self.ops["locked_commit"] = {"login": "committer", "result": pending}
        self.statements["locked_commit"] = bind(key, checked)
        self.select("select_after_commit", "v0")

    def evidence(self):
        sql = "SELECT jsonb_build_object(" + ", ".join(
            f"'{table}', (SELECT COALESCE(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)), '[]') FROM {table} t)"
            for table in COUNTS) + ");"
        records = self.use("collect", "observer", sql, parse=True, record=False)
        # Persist logical cross-checks derived from live server logs, excluding volatile
        # per-process metadata and credentials. Roles provisioned before logging.
        lines = self.db.log.read_text().splitlines()
        checks = {}
        indexes = {}
        for tag, sql in self.statements.items():
            role = self.ops[tag]["login"]
            prefix = f" {role} postgres {self.name}/{tag} LOG: "
            rows = sql.lstrip().splitlines()
            statement = rows[-1] if tag == "competing_select_while_locked" else rows[0]
            matches = [i for i, line in enumerate(lines) if prefix in line and "statement: " + statement in line]
            assert len(matches) == 1, (tag, statement, [line for line in lines if prefix in line])
            indexes[tag] = matches[0]
            checks[tag] = role
        if self.name == "c03":
            assert indexes["publish"] < indexes["revoke_writer"] < indexes["select_old_publication"] < indexes["real"]
        return records, {"logged_statement_actor": checks}


def bind(token, checked):
    return f"SELECT bind_decision('{token}','{checked['version']}',{checked['epoch']});"


def scenario(attempt):
    name = attempt.name
    privileges_before = attempt.privileges("privileges_before")
    assert privileges_before["writer"]["MayCreateVersion"]
    assert not privileges_before["writer"]["MaySelectVersion"]
    assert privileges_before["selector"]["MaySelectVersion"]
    assert not privileges_before["selector"]["MayCreateVersion"]
    assert all(not privileges_before[role]["MayModifyCriterion"] for role in ROLES)
    if name == "c00":
        attempt.select("select_control", "v0")
    else:
        attempt.publish()

    if name == "c01":
        attempt.select("writer_select_denied", "v1", error="42501")
        attempt.use("writer_edit_denied", "writer", "UPDATE criteria SET threshold=1 WHERE version='v0';",
                    error="42501")
    if name == "c02":
        attempt.use("selector_create_denied", "selector",
                    "INSERT INTO criteria(version,threshold) VALUES ('v2',1);", error="42501")
        attempt.use("selector_edit_denied", "selector",
                    "UPDATE criteria SET threshold=0 WHERE version='v1';", error="42501")
        attempt.select("select_base", "v0")
        assert attempt.evaluate("base")["accepted"]
        attempt.select("select_alternative", "v1")
    if name == "c03":
        attempt.use("revoke_writer", ADMIN, "REVOKE INSERT(version,threshold) ON criteria FROM writer;")
        assert not attempt.privileges("privileges_after_revoke")["writer"]["MayCreateVersion"]
        attempt.use("revoked_insert_denied", "writer",
                    "INSERT INTO criteria(version,threshold) VALUES ('v2',1);", error="42501")
        attempt.select("select_old_publication", "v1")

    checked = attempt.check("checked")
    if name == "c04":
        attempt.evaluate("stale")
        attempt.select("switch", "v1")
        assert attempt.evaluate("racy")["version"] == "v1"
        attempt.finish("racy_commit_denied", "racy", checked, error="23514")
        attempt.finish("stale_commit_denied", "stale", checked, error="40001")
        assert attempt.use("no_stale_decisions", "observer", "SELECT count(*) FROM decisions;") == "0"
        fresh = attempt.check("fresh_checked")
        attempt.evaluate("fresh")
        attempt.use("missing_check_denied", "committer",
                    "SELECT bind_decision('fresh',NULL,NULL);", error="23514")
        attempt.locked_commit("fresh", fresh)
        return

    result = attempt.evaluate("real")
    if name == "c00":
        attempt.finish("adjudicator_commit_denied", "real", checked, error="42501", role="adjudicator")
        attempt.use("committer_direct_insert_denied", "committer",
                    "INSERT INTO decisions VALUES ('real','v0',1,true);", error="42501")
    assert result["version"] == checked["version"]
    attempt.finish("commit", "real", checked)


def reference(name, records):
    """Use predeclared fixture values and independent digest/arithmetic checks."""
    expected = {
        "c00": ("v0", 0, "real"), "c01": ("v0", 0, "real"),
        "c02": ("v1", 1, "real"), "c03": ("v1", 1, "real"), "c04": ("v1", 1, "fresh"),
    }
    version, threshold, token = expected[name]
    entry = next(row for row in records["criteria"] if row["version"] == version)
    event_by_epoch = {row["epoch"]: row for row in records["selection_events"]}
    finals = records["decisions"]
    assert len(finals) == 1
    final = finals[0]
    calc = hashlib.sha256(threshold.to_bytes(2, "big", signed=True)).hexdigest()
    score = records["sealed_score"][0]
    assert score == {"id": "x@1", "value": 0}
    assert entry["threshold"] == threshold and entry["digest"] == calc
    ev = next(row for row in records["evaluations"] if row["token"] == token)
    assert (ev["epoch"], ev["version"], ev["digest"], ev["accepted"], ev["actor"], ev["policy"]) == (
        final["epoch"], version, calc, threshold == 0, "adjudicator", "ge@1")
    assert (final["token"], final["version"], final["accepted"], final["actor"]) == (
        token, version, threshold == 0, "committer")
    selection = event_by_epoch[ev["epoch"]]
    assert selection["version"] == version
    assert selection["actor"] == (ADMIN if name == "c01" else "selector")
    if name in ("c02", "c03", "c04"):
        assert entry["author"] == "writer"
        assert int(entry["publication_xid"]) < int(selection["xid"])
    # Strip engine transaction IDs only after independently checking their
    # relative publication/selection order. They are allocated per cluster.
    return {"independent_digest_match": True, "arithmetic_and_commit_match": True,
            "consumed": version, "selected_by": selection["actor"],
            "published_by": entry["author"], "threshold": threshold}


def chain(name):
    # Statuses apply to the bounded trusted-server model and verified controls.
    result = {
        "principal_to_permission": "VERIFIED",
        "permission_to_operation": "VERIFIED",
        "operation_to_resolver_state": "VERIFIED",
        "resolver_state_to_consumed_version": "VERIFIED",
        "consumed_version_to_persisting_writer_effect": (
            "VERIFIED" if name in ("c02", "c03", "c04") else "NOT OBSERVABLE"),
        "consumed_version_to_commit": "VERIFIED",
    }
    if name == "c01":
        result["writer_to_unauthorized_selection"] = "CONTRADICTED"
    if name == "c04":
        result["stale_or_unchecked_use_to_commit"] = "CONTRADICTED"
    result["absence_of_out_of_scope_mutation_or_missing_events"] = "UNKNOWN"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribution", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("run with assertions enabled")
    attempts, costs = {}, {}
    with database(args.distribution.resolve()) as db:
        version, _ = db.query("observer", None, "SHOW server_version;")
        assert version == "17.11 (Debian 17.11-0+deb13u1)", version
        for i in range(5):
            name = f"c{i:02}"
            attempt = Attempt(db, name)
            scenario(attempt)
            evidence, log = attempt.evidence()
            verified = reference(name, evidence)
            for table in ("criteria", "selection_events"):
                for row in evidence[table]:
                    row.pop("publication_xid", None)
                    row.pop("xid", None)
            attempts[name.upper()] = {"E1_client_operations": attempt.ops, "E2_server_rows": evidence,
                                      "E2_server_log_checks": log, "E3_assessor_checks": verified,
                                      "chain": chain(name)}
            costs[name.upper()] = attempt.times
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"status": "EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION",
              "postgresql": version, "cases": attempts}
    (args.out / "RESULTS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (args.out / "MEASUREMENTS.json").write_text(json.dumps(costs, indent=2, sort_keys=True) + "\n")
    print("PASS: C00–C04, separate authenticated roles, native ACL controls, stale-commit rejection and lock contention")


if __name__ == "__main__":
    main()
