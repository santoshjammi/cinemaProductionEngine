"""Unit tests for movie_os.genesis.session.SessionManager."""

from __future__ import annotations

import json

import pytest

from movie_os.genesis.session import SessionManager


class TestSessionLifecycle:
    def test_create_session(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("A synopsis")
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_create_session_with_constraints(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("S", {"runtime": "15min"})
        session = sm.get_session(sid)
        assert session is not None
        assert session["constraints"] == {"runtime": "15min"}

    def test_get_session_missing(self, session_db_path):
        sm = SessionManager(session_db_path)
        assert sm.get_session("nonexistent") is None

    def test_create_multiple_sessions_unique_ids(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid1 = sm.create_session("S1")
        sid2 = sm.create_session("S2")
        assert sid1 != sid2


class TestSessionStage:
    def test_default_stage(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("S")
        assert sm.get_session(sid)["stage"] == "init"

    def test_update_stage(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("S")
        sm.update_stage(sid, "discovery")
        assert sm.get_session(sid)["stage"] == "discovery"
        sm.update_stage(sid, "complete")
        assert sm.get_session(sid)["stage"] == "complete"

    def test_update_stage_missing_does_nothing(self, session_db_path):
        sm = SessionManager(session_db_path)
        # Should not raise
        sm.update_stage("nonexistent", "discovery")

    def test_set_pkg_path(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("S")
        sm.set_pkg_path(sid, "/tmp/test.db")
        session = sm.get_session(sid)
        assert session["pkg_path"] == "/tmp/test.db"


class TestSessionListing:
    def test_list_empty(self, session_db_path):
        sm = SessionManager(session_db_path)
        assert sm.list_sessions() == []

    def test_list_returns_all(self, session_db_path):
        sm = SessionManager(session_db_path)
        sm.create_session("First synopsis that is long enough to maybe truncate")
        sm.create_session("Second")
        sessions = sm.list_sessions()
        assert len(sessions) == 2

    def test_list_includes_summary(self, session_db_path):
        sm = SessionManager(session_db_path)
        sid = sm.create_session("A short synopsis")
        sessions = sm.list_sessions()
        assert len(sessions) == 1
        s = sessions[0]
        assert s["session_id"] == sid
        assert s["synopsis"] == "A short synopsis"
        assert s["stage"] == "init"

    def test_list_truncates_long_synopsis(self, session_db_path):
        sm = SessionManager(session_db_path)
        sm.create_session("x" * 200)
        sessions = sm.list_sessions()
        assert sessions[0]["synopsis"].endswith("...")


class TestSessionClose:
    def test_close_idempotent(self, session_db_path):
        sm = SessionManager(session_db_path)
        sm.create_session("S")
        sm.close()
        sm.close()  # no error
