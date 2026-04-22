"""config_diff.py のテスト"""

import pytest
from config_diff import SectionDiff, detect_format, diff_sections, parse_config, parse_juniper_sections, parse_sections


# ---------------------------------------------------------------------------
# parse_sections
# ---------------------------------------------------------------------------

class TestParseSections:
    def test_parses_basic_sections(self):
        text = "interface Gi0/0\n ip address 1.1.1.1\n no shutdown\nrouter ospf 1\n network 1.0.0.0"
        secs = parse_sections(text)
        assert "interface Gi0/0" in secs
        assert "router ospf 1" in secs

    def test_indented_lines_belong_to_section(self):
        text = "interface Gi0/0\n ip address 1.1.1.1\n no shutdown"
        secs = parse_sections(text)
        assert " ip address 1.1.1.1" in secs["interface Gi0/0"].lines
        assert " no shutdown" in secs["interface Gi0/0"].lines

    def test_comment_lines_attached_to_current_section(self):
        text = "interface Gi0/0\n ip address 1.1.1.1\n!\nrouter ospf 1"
        secs = parse_sections(text)
        assert "!" in secs["interface Gi0/0"].lines

    def test_empty_text_returns_empty(self):
        assert parse_sections("") == {}

    def test_blank_lines_ignored_at_top_level(self):
        text = "\n\ninterface Gi0/0\n ip address 1.1.1.1"
        secs = parse_sections(text)
        assert len(secs) == 1

    def test_hash_comment_ignored(self):
        text = "# comment\ninterface Gi0/0\n ip address 1.1.1.1"
        secs = parse_sections(text)
        assert len(secs) == 1


# ---------------------------------------------------------------------------
# diff_sections
# ---------------------------------------------------------------------------

BEFORE_TEXT = """\
hostname Router-A
interface Gi0/0
 ip address 192.168.1.1 255.255.255.0
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
ip access-list extended ACL-WEB
 permit tcp any any eq 80
"""

AFTER_TEXT = """\
hostname Router-A
interface Gi0/0
 ip address 192.168.1.1 255.255.255.0
 ip helper-address 10.0.0.10
interface Loopback0
 ip address 172.16.0.1 255.255.255.255
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
ip access-list extended ACL-WEB
 permit tcp any any eq 80
 permit tcp any any eq 443
"""


class TestDiffSections:
    def setup_method(self):
        self.before = parse_sections(BEFORE_TEXT)
        self.after = parse_sections(AFTER_TEXT)

    def _find(self, diffs: list[SectionDiff], name: str) -> SectionDiff | None:
        return next((d for d in diffs if d.name == name), None)

    def test_unchanged_section_detected(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "hostname Router-A")
        assert d is not None
        assert d.status == "unchanged"

    def test_changed_section_detected(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "interface Gi0/0")
        assert d is not None
        assert d.status == "changed"

    def test_added_section_detected(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "interface Loopback0")
        assert d is not None
        assert d.status == "added"

    def test_removed_section_detected(self):
        # before だけにあるセクション
        before = parse_sections("router bgp 65000\n neighbor 1.1.1.1\n")
        after = parse_sections("hostname R1\n")
        diffs = diff_sections(before, after)
        d = self._find(diffs, "router bgp 65000")
        assert d is not None
        assert d.status == "removed"

    def test_unified_diff_populated_for_changed(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "interface Gi0/0")
        assert d is not None
        assert len(d.unified_diff) > 0

    def test_unified_diff_empty_for_unchanged(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "hostname Router-A")
        assert d is not None
        assert d.unified_diff == []

    def test_filter_keyword_limits_results(self):
        diffs = diff_sections(self.before, self.after, filter_keyword="interface")
        names = [d.name for d in diffs]
        assert all("interface" in n.lower() for n in names)

    def test_filter_keyword_case_insensitive(self):
        diffs = diff_sections(self.before, self.after, filter_keyword="INTERFACE")
        assert len(diffs) > 0

    def test_filter_keyword_none_returns_all(self):
        diffs_all = diff_sections(self.before, self.after)
        diffs_none = diff_sections(self.before, self.after, filter_keyword=None)
        assert len(diffs_all) == len(diffs_none)

    def test_acl_section_changed(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "ip access-list extended ACL-WEB")
        assert d is not None
        assert d.status == "changed"

    def test_ospf_section_unchanged(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "router ospf 1")
        assert d is not None
        assert d.status == "unchanged"

    def test_empty_before_all_added(self):
        diffs = diff_sections({}, self.after)
        assert all(d.status == "added" for d in diffs)

    def test_empty_after_all_removed(self):
        diffs = diff_sections(self.before, {})
        assert all(d.status == "removed" for d in diffs)

    def test_to_dict_contains_required_keys(self):
        diffs = diff_sections(self.before, self.after)
        d = diffs[0].to_dict()
        assert set(d.keys()) == {"name", "status", "before_lines", "after_lines", "unified_diff"}


# ---------------------------------------------------------------------------
# parse_juniper_sections
# ---------------------------------------------------------------------------

JUNIPER_TEXT = """\
version 22.4R1;
system {
    host-name Router-A;
    login {
        user admin {
            class super-user;
        }
    }
}
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 192.168.1.1/24;
            }
        }
    }
}
routing-options {
    router-id 192.168.1.1;
    autonomous-system 65000;
}
firewall {
    filter ACL-WEB {
        term PERMIT-HTTP {
            from {
                destination-port [http https];
            }
            then accept;
        }
    }
}
"""


class TestParseJuniperSections:
    def test_top_level_blocks_detected(self):
        secs = parse_juniper_sections(JUNIPER_TEXT)
        assert "system" in secs
        assert "interfaces" in secs
        assert "routing-options" in secs
        assert "firewall" in secs

    def test_single_line_statement_detected(self):
        secs = parse_juniper_sections(JUNIPER_TEXT)
        assert "version 22.4R1" in secs

    def test_block_content_captured(self):
        secs = parse_juniper_sections(JUNIPER_TEXT)
        combined = "\n".join(secs["interfaces"].lines)
        assert "ge-0/0/0" in combined
        assert "192.168.1.1/24" in combined

    def test_nested_blocks_not_split_as_sections(self):
        secs = parse_juniper_sections(JUNIPER_TEXT)
        # ge-0/0/0 はトップレベルでないのでセクションにならない
        assert "ge-0/0/0" not in secs

    def test_comment_lines_skipped(self):
        text = "# comment\ninterfaces {\n    ge-0/0/0 {\n    }\n}\n"
        secs = parse_juniper_sections(text)
        assert len(secs) == 1
        assert "interfaces" in secs

    def test_empty_text_returns_empty(self):
        assert parse_juniper_sections("") == {}

    def test_multiple_blocks_all_captured(self):
        secs = parse_juniper_sections(JUNIPER_TEXT)
        assert len(secs) >= 4


# ---------------------------------------------------------------------------
# detect_format
# ---------------------------------------------------------------------------

class TestDetectFormat:
    def test_cisco_detected_by_bang_comments(self):
        text = "!\nhostname R1\n!\ninterface Gi0/0\n ip address 1.1.1.1\n!\n"
        assert detect_format(text) == "cisco"

    def test_juniper_detected_by_braces(self):
        text = "system {\n    host-name R1;\n}\ninterfaces {\n    ge-0/0/0 {\n    }\n}\n"
        assert detect_format(text) == "juniper"

    def test_empty_text_defaults_to_cisco(self):
        assert detect_format("") == "cisco"


# ---------------------------------------------------------------------------
# parse_config
# ---------------------------------------------------------------------------

class TestParseConfig:
    def test_auto_detects_cisco(self):
        text = "!\nhostname R1\n!\ninterface Gi0/0\n ip address 1.1.1.1\n!\n"
        _, fmt = parse_config(text)
        assert fmt == "cisco"

    def test_auto_detects_juniper(self):
        _, fmt = parse_config(JUNIPER_TEXT)
        assert fmt == "juniper"

    def test_explicit_format_overrides_auto(self):
        # Cisco テキストを juniper として解析するよう強制
        text = "!\nhostname R1\n"
        _, fmt = parse_config(text, fmt="juniper")
        assert fmt == "juniper"

    def test_returns_sections_dict(self):
        secs, _ = parse_config(JUNIPER_TEXT)
        assert isinstance(secs, dict)
        assert len(secs) > 0


# ---------------------------------------------------------------------------
# Juniper diff
# ---------------------------------------------------------------------------

JUNIPER_BEFORE = """\
system {
    host-name Router-A;
}
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 192.168.1.1/24;
            }
        }
    }
}
firewall {
    filter ACL-WEB {
        term PERMIT-HTTP {
            from {
                destination-port [http https];
            }
            then accept;
        }
    }
}
"""

JUNIPER_AFTER = """\
system {
    host-name Router-A;
    ntp {
        server 10.0.0.1;
    }
}
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 192.168.1.1/24;
            }
        }
    }
    lo0 {
        unit 0 {
            family inet {
                address 172.16.0.1/32;
            }
        }
    }
}
firewall {
    filter ACL-WEB {
        term PERMIT-HTTP {
            from {
                destination-port [http https 8080];
            }
            then accept;
        }
    }
}
"""


class TestJuniperDiff:
    def setup_method(self):
        self.before = parse_juniper_sections(JUNIPER_BEFORE)
        self.after = parse_juniper_sections(JUNIPER_AFTER)

    def _find(self, diffs: list[SectionDiff], name: str) -> SectionDiff | None:
        return next((d for d in diffs if d.name == name), None)

    def test_system_changed(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "system")
        assert d is not None
        assert d.status == "changed"

    def test_interfaces_changed(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "interfaces")
        assert d is not None
        assert d.status == "changed"

    def test_firewall_changed(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "firewall")
        assert d is not None
        assert d.status == "changed"

    def test_filter_by_firewall(self):
        diffs = diff_sections(self.before, self.after, filter_keyword="firewall")
        assert len(diffs) == 1
        assert diffs[0].name == "firewall"

    def test_unified_diff_shows_lo0_added(self):
        diffs = diff_sections(self.before, self.after)
        d = self._find(diffs, "interfaces")
        assert d is not None
        added_lines = [ln for ln in d.unified_diff if ln.startswith("+")]
        assert any("lo0" in ln for ln in added_lines)
