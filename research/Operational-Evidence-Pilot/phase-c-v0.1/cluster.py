"""Unprivileged isolated PostgreSQL launcher and test connection client."""
from contextlib import contextmanager
import os
from pathlib import Path
import secrets
import socket
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter_ns

ROLES = ("writer", "selector", "adjudicator", "committer", "observer")
ADMIN = "pilot_admin"


class Cluster:
    def __init__(self, distribution, root):
        self.bin = distribution / "usr/lib/postgresql/17/bin"
        self.env = {"PATH": os.environ["PATH"], "LD_LIBRARY_PATH": str(distribution / "usr/lib/x86_64-linux-gnu"),
                    "LC_ALL": "C", "PGHOST": "127.0.0.1", "PGDATABASE": "postgres",
                    "PGSSLMODE": "disable", "PGGSSENCMODE": "disable", "PGCONNECT_TIMEOUT": "3"}
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.env["PGPORT"] = port = str(sock.getsockname()[1])
        self.passwords = {role: secrets.token_hex(24) for role in (ADMIN, *ROLES)}
        self.data, self.log = root / "data", root / "server.log"
        secret = os.open(root / "pw", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(secret, "w") as handle:
            handle.write(self.passwords[ADMIN] + "\n")
        self.tool("initdb", "-D", self.data, "--auth-local=reject", "--auth-host=scram-sha-256",
                  "-U", ADMIN, f"--pwfile={root / 'pw'}", "--no-locale", "--encoding=UTF8")
        (root / "pw").unlink()
        # Hide role provisioning statements. Enable audit once identities exist.
        self.tool("pg_ctl", "-D", self.data, "-l", self.log, "-o",
                  f"-c listen_addresses=127.0.0.1 -c unix_socket_directories= -p {port}", "-w", "start")

    def tool(self, command, *args):
        return subprocess.run([self.bin / command, *args], check=True, env=self.env,
                              capture_output=True, timeout=30)

    def command(self, role, app='phase-c'):
        return [self.bin / "psql", "-XqAt", "-U", role, "-v", "ON_ERROR_STOP=1",
                "-v", "VERBOSITY=verbose"], {**self.env, "PGPASSWORD": self.passwords[role], "PGAPPNAME": app}

    def query(self, role, schema, sql, error=None, app='phase-c'):
        cmd, env = self.command(role, app)
        prefix = f"SET search_path TO {schema},pg_catalog;\n" if schema else ""
        start = perf_counter_ns()
        run = subprocess.run(cmd, env=env, input=prefix + sql + "\n", text=True,
                             capture_output=True, timeout=8)
        elapsed = (perf_counter_ns() - start) / 1e6
        if error is not None:
            if run.returncode == 0 or f"{error}:" not in run.stderr:
                raise AssertionError(f"expected {error}, rc={run.returncode}: {run.stderr}")
            return {"sqlstate": error, "message": run.stderr.splitlines()[0].split(": ", 2)[-1]}, elapsed
        if run.returncode:
            raise RuntimeError(run.stderr)
        return run.stdout.strip(), elapsed

    def provision(self):
        statements = [f"CREATE ROLE {role} LOGIN PASSWORD '{self.passwords[role]}';" for role in ROLES]
        self.query(ADMIN, None, "\n".join(statements))
        with (self.data / "postgresql.conf").open("a") as config:
            config.write("\nlog_statement = 'all'\nlog_line_prefix = '%m [%p] %u %d %a '\n")
        self.tool("pg_ctl", "-D", self.data, "-w", "restart", "-m", "fast", "-l", self.log)

    def stop(self):
        self.tool("pg_ctl", "-D", self.data, "-m", "immediate", "-w", "stop")


@contextmanager
def database(distribution):
    with TemporaryDirectory(prefix="dea-c-") as temporary:
        cluster = Cluster(distribution, Path(temporary))
        try:
            cluster.provision()
            yield cluster
        finally:
            cluster.stop()
