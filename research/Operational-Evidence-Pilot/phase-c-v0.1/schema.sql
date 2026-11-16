BEGIN;
CREATE SCHEMA @NS@;
SET search_path = @NS@, pg_catalog;
REVOKE ALL ON SCHEMA @NS@ FROM PUBLIC;
GRANT USAGE ON SCHEMA @NS@ TO writer, selector, adjudicator, committer, observer;

CREATE TABLE criteria (
    version text PRIMARY KEY,
    threshold smallint NOT NULL CHECK (threshold IN (0, 1)),
    author name NOT NULL DEFAULT SESSION_USER,
    publication_xid xid8 NOT NULL DEFAULT pg_current_xact_id(),
    digest text GENERATED ALWAYS AS (encode(sha256(int2send(threshold)), 'hex')) STORED
);
CREATE TABLE sealed_score (
    id text PRIMARY KEY,
    value smallint NOT NULL CHECK (value BETWEEN 0 AND 3)
);
CREATE TABLE active (
    singleton boolean PRIMARY KEY CHECK (singleton),
    version text NOT NULL REFERENCES criteria,
    epoch bigint NOT NULL
);
CREATE TABLE selection_events (
    epoch bigint PRIMARY KEY,
    old_version text REFERENCES criteria,
    version text NOT NULL REFERENCES criteria,
    actor name NOT NULL DEFAULT SESSION_USER,
    xid xid8 NOT NULL DEFAULT pg_current_xact_id()
);
CREATE TABLE evaluations (
    token text PRIMARY KEY,
    score_id text NOT NULL REFERENCES sealed_score,
    policy text NOT NULL CHECK (policy = 'ge@1'),
    version text NOT NULL REFERENCES criteria,
    epoch bigint NOT NULL REFERENCES selection_events,
    digest text NOT NULL,
    accepted boolean NOT NULL,
    actor name NOT NULL DEFAULT SESSION_USER
);
CREATE TABLE decisions (
    token text PRIMARY KEY REFERENCES evaluations,
    version text NOT NULL REFERENCES criteria,
    epoch bigint NOT NULL REFERENCES selection_events,
    accepted boolean NOT NULL,
    actor name NOT NULL DEFAULT SESSION_USER
);
INSERT INTO criteria(version, threshold) VALUES ('v0', 0);
INSERT INTO sealed_score VALUES ('x@1', 0);
INSERT INTO active VALUES (true, 'v0', 0);
INSERT INTO selection_events(epoch, old_version, version) VALUES (0, NULL, 'v0');

CREATE FUNCTION record_selection() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, @NS@, pg_temp AS $$
BEGIN
    NEW.epoch := OLD.epoch + 1;
    INSERT INTO selection_events(epoch, old_version, version) VALUES (NEW.epoch, OLD.version, NEW.version);
    RETURN NEW;
END;
$$;
CREATE TRIGGER record_selection BEFORE UPDATE OF version ON active
FOR EACH ROW EXECUTE FUNCTION record_selection();

-- A single SQL statement consumes the selected version and writes its result.
CREATE FUNCTION evaluate(request_token text) RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path = pg_catalog, @NS@, pg_temp AS $$
    INSERT INTO evaluations(token, score_id, policy, version, epoch, digest, accepted)
    SELECT request_token, s.id, 'ge@1', c.version, a.epoch, c.digest, s.value >= c.threshold
    FROM active a JOIN criteria c USING (version) CROSS JOIN sealed_score s
    RETURNING to_jsonb(evaluations);
$$;

-- Lock the same row that the selector updates, check both observations and write
-- the final decision in the lock-holding transaction.
CREATE FUNCTION bind_decision(request_token text, checked_version text, checked_epoch bigint)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, @NS@, pg_temp AS $$
DECLARE choice active%ROWTYPE; assessed evaluations%ROWTYPE; decision decisions%ROWTYPE;
BEGIN
    SELECT * INTO STRICT choice FROM active WHERE singleton FOR UPDATE;
    SELECT * INTO STRICT assessed FROM evaluations WHERE token = request_token;
    IF assessed.version IS DISTINCT FROM checked_version OR assessed.epoch IS DISTINCT FROM checked_epoch THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'checked version differs from consumed version';
    END IF;
    IF choice.version IS DISTINCT FROM assessed.version OR choice.epoch IS DISTINCT FROM assessed.epoch THEN
        RAISE EXCEPTION USING ERRCODE = '40001', MESSAGE = 'selected version changed after evaluation';
    END IF;
    INSERT INTO decisions(token, version, epoch, accepted)
    VALUES (request_token, assessed.version, assessed.epoch, assessed.accepted)
    RETURNING * INTO decision;
    RETURN to_jsonb(decision);
END;
$$;

REVOKE ALL ON ALL FUNCTIONS IN SCHEMA @NS@ FROM PUBLIC;
GRANT INSERT(version, threshold) ON criteria TO writer;
GRANT SELECT ON criteria TO writer, selector, adjudicator;
GRANT SELECT ON active TO writer, selector, adjudicator;
GRANT UPDATE(version) ON active TO selector;
GRANT EXECUTE ON FUNCTION evaluate(text) TO adjudicator;
GRANT EXECUTE ON FUNCTION bind_decision(text, text, bigint) TO committer;
GRANT SELECT ON ALL TABLES IN SCHEMA @NS@ TO observer;
COMMIT;
