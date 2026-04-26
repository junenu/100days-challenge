"""Tests for log_analyzer.py."""

import unittest

from log_analyzer import (
    http_status,
    parse_log_line,
    parse_log_text,
    positive_int,
    render_summary,
    summarize,
)


VALID_LINE = (
    '192.168.10.11 - - [26/Apr/2026:09:00:03 +0900] '
    '"GET /docs HTTP/1.1" 200 4096'
)


class ParseLogLineTest(unittest.TestCase):
    def test_parses_valid_line(self):
        entry = parse_log_line(VALID_LINE)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.ip, "192.168.10.11")
        self.assertEqual(entry.method, "GET")
        self.assertEqual(entry.path, "/docs")
        self.assertEqual(entry.status, 200)
        self.assertEqual(entry.size, 4096)

    def test_returns_none_for_invalid_line(self):
        self.assertIsNone(parse_log_line("this is not an access log"))

    def test_size_dash_becomes_none(self):
        line = (
            '192.168.10.11 - - [26/Apr/2026:09:00:03 +0900] '
            '"GET /docs HTTP/1.1" 200 -'
        )
        entry = parse_log_line(line)

        self.assertIsNotNone(entry)
        self.assertIsNone(entry.size)


class ParseLogTextTest(unittest.TestCase):
    def test_collects_entries_and_skipped_lines(self):
        result = parse_log_text(f"{VALID_LINE}\ninvalid\n")

        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.skipped_lines, [(2, "invalid")])

    def test_status_filter_keeps_matching_entries_only(self):
        text = "\n".join(
            [
                VALID_LINE,
                '192.168.10.12 - - [26/Apr/2026:09:01:03 +0900] "GET /x HTTP/1.1" 404 12',
            ]
        )
        result = parse_log_text(text, status_filter=404)

        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.entries[0].status, 404)


class SummaryTest(unittest.TestCase):
    def test_summarizes_status_path_ip_method_and_hour(self):
        text = "\n".join(
            [
                VALID_LINE,
                '192.168.10.12 - - [26/Apr/2026:09:01:03 +0900] "GET /docs HTTP/1.1" 200 12',
                '192.168.10.12 - - [26/Apr/2026:10:01:03 +0900] "POST /api HTTP/1.1" 500 12',
                "broken",
            ]
        )
        result = parse_log_text(text)
        summary = summarize(result.entries, skipped_count=len(result.skipped_lines))

        self.assertEqual(summary.total_requests, 3)
        self.assertEqual(summary.status_counts[200], 2)
        self.assertEqual(summary.path_counts["/docs"], 2)
        self.assertEqual(summary.ip_counts["192.168.10.12"], 2)
        self.assertEqual(summary.method_counts["GET"], 2)
        self.assertEqual(summary.hourly_counts["2026-04-26 09:00"], 2)
        self.assertEqual(summary.skipped_count, 1)

    def test_render_summary_includes_filter_and_rankings(self):
        result = parse_log_text(VALID_LINE)
        summary = summarize(result.entries)
        output = render_summary(summary, top=3, status_filter=200)

        self.assertIn("Filter: status=200", output)
        self.assertIn("Total requests: 1", output)
        self.assertIn("/docs", output)


class ArgumentTypeTest(unittest.TestCase):
    def test_positive_int_accepts_positive_number(self):
        self.assertEqual(positive_int("3"), 3)

    def test_http_status_accepts_valid_status(self):
        self.assertEqual(http_status("404"), 404)

    def test_http_status_rejects_out_of_range_status(self):
        with self.assertRaises(Exception):
            http_status("99")


if __name__ == "__main__":
    unittest.main()
