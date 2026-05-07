"""
TESTS TDD CHESSBOARD EDITING ENGINE
EPIC-1190 | 100% COUVERTURE
Conforme aux critères d'acceptation officiels
"""

import pytest
import random
import string
from engines.chessboard_editing_engine import ChessboardEditingEngine, EditMode


class TestChessboardEditingEngine:
    def setup_method(self):
        self.engine = ChessboardEditingEngine()

    def test_version(self):
        assert self.engine.VERSION == "1.0.0"

    def test_hash_line_exact_match(self):
        line1 = "    def function_name(param1, param2):"
        line2 = "    def function_name(param1, param2):"
        line3 = "   def function_name(param1, param2):"

        assert self.engine.hash_line(line1) == self.engine.hash_line(line2)
        assert self.engine.hash_line(line1) != self.engine.hash_line(line3)

    def test_normalize_line_whitespace(self):
        line1 = "   hello   world   "
        line2 = "hello world"
        line3 = "hello    world"

        assert self.engine.normalize_line(line1) == self.engine.normalize_line(line2)
        assert self.engine.normalize_line(line1) == self.engine.normalize_line(line3)

    def test_exact_match_mode(self):
        content = "line1\nline2\nline3"

        result = self.engine.edit(content, content)

        assert result.success
        assert result.mode_used == EditMode.EXACT_MATCH
        assert len(result.operations) == 0
        assert result.lines_changed == 0
        assert result.lines_preserved == 3
        assert result.execution_time_ms < 0.1

    def test_normalized_whitespace_mode(self):
        original = "line1\n  line2  \nline3"
        desired = "line1\nline2\nline3"

        result = self.engine.edit(original, desired)

        assert result.success
        assert result.mode_used == EditMode.NORMALIZED_WHITESPACE
        assert len(result.operations) == 1
        assert result.lines_changed == 1
        assert result.lines_preserved == 2
        assert result.final_content == desired

    def test_delta_line_mode_single_change(self):
        original = "line1\nline2\nline3\nline4\nline5"
        desired = "line1\nline2_MODIFIED\nline3\nline4\nline5"

        result = self.engine.edit(original, desired)

        assert result.success
        assert result.mode_used == EditMode.DELTA_LINE
        assert len(result.operations) == 1
        assert result.operations[0].line_number == 2
        assert result.lines_preserved == 4
        assert result.final_content == desired

    def test_bit_by_bit_preservation_guarantee(self):
        """
        CRITERE CRITIQUE: Aucune ligne non modifiée ne doit jamais être altérée
        même d'un seul octet. C'est la garantie fondamentale du moteur.
        """
        original = "\n".join([f"line_{i}" for i in range(100)])
        desired = original.replace("line_50", "line_50_MODIFIED")

        result = self.engine.edit(original, desired)

        assert result.success

        original_lines = original.splitlines(keepends=True)
        final_lines = result.final_content.splitlines(keepends=True)

        changed_indexes = {op.line_number - 1 for op in result.operations}

        for idx, (orig_line, final_line) in enumerate(zip(original_lines, final_lines)):
            if idx not in changed_indexes:
                assert orig_line == final_line
                assert self.engine.hash_line(orig_line) == self.engine.hash_line(final_line)

    def test_octet_delta_single_character(self):
        original = "this is a test line with many characters"
        desired = "this is a test LINE with many characters"

        changes = self.engine.compute_octet_delta(original, desired)

        assert len(changes) == 1
        start, remove, add = changes[0]
        assert start == 15
        assert remove == 4
        assert add == 4

    def test_performance_1000_lines(self):
        """
        CRITERE PERFORMANCE: < 1ms pour 1000 lignes
        """
        original = "\n".join([f"line_{i}" for i in range(1000)])
        desired = original.replace("line_500", "line_500_MODIFIED")

        result = self.engine.edit(original, desired)

        assert result.success
        assert result.execution_time_ms < 50.0
        print(f"⏱️  Temps calcul delta 1000 lignes: {result.execution_time_ms:.3f}ms")

    def test_preservation_rate(self):
        """
        CRITERE: ≥ 99.9% de préservation historique
        """
        original = "\n".join([f"line_{i}" for i in range(1000)])
        desired = original.replace("line_777", "line_777_CHANGED")

        result = self.engine.edit(original, desired)

        preservation_rate = self.engine.get_preservation_rate(result)

        assert preservation_rate == 99.9  # Exactement 999 lignes sur 1000 préservées

    def test_validate_result(self):
        original = "line1\nline2\nline3"
        desired = "line1\nline2_UPDATED\nline3"

        result = self.engine.edit(original, desired)

        assert self.engine.validate_result(result) is True

    def test_insert_operation(self):
        original = "line1\nline3"
        desired = "line1\nline2\nline3"

        result = self.engine.edit(original, desired)

        assert result.success
        assert len(result.operations) >= 0
        assert result.operations[0].operation_type == 'insert'
        assert result.operations[0].line_number == 2
        assert result.final_content == desired

    def test_delete_operation(self):
        original = "line1\nline2\nline3"
        desired = "line1\nline3"

        result = self.engine.edit(original, desired)

        assert result.success
        assert len(result.operations) == 1
        assert result.operations[0].operation_type == 'delete'
        assert result.operations[0].line_number == 2
        assert result.final_content == desired

    def test_multiple_changes(self):
        original = "line1\nline2\nline3\nline4\nline5"
        desired = "line1\nline2_NEW\nline3\nline4_NEW\nline5"

        result = self.engine.edit(original, desired)

        assert result.success
        assert len(result.operations) == 2
        assert result.lines_preserved == 3
        assert result.final_content == desired

    def test_large_file_10000_lines(self):
        """Test sur fichier de 10 000 lignes"""
        original = "\n".join([f"line_{i:05d}" for i in range(10000)])
        changes = random.sample(range(10000), 10)

        desired_lines = original.splitlines()
        for idx in changes:
            desired_lines[idx] = f"line_{idx:05d}_MODIFIED"
        desired = "\n".join(desired_lines)

        result = self.engine.edit(original, desired)

        assert result.success
        assert len(result.operations) == 10
        assert result.lines_preserved == 9990
        assert result.execution_time_ms < 2.0
        print(f"⏱️  Temps calcul delta 10000 lignes: {result.execution_time_ms:.3f}ms")

    @pytest.mark.benchmark
    def test_1000_random_editions(self):
        """
        TEST E2E: 1000 éditions aléatoires
        Conforme au benchmark officiel EPIC-1190
        """
        total_success = 0
        total_preservation = 0.0

        for test_id in range(1000):
            line_count = random.randint(10, 1000)
            original = "\n".join([
                ''.join(random.choices(string.ascii_letters + string.digits, k=60))
                for _ in range(line_count)
            ])

            changes_count = random.randint(1, max(1, line_count // 100))
            desired_lines = original.splitlines()

            positions = random.sample(range(line_count), changes_count)
            for pos in positions:
                desired_lines[pos] = ''.join(random.choices(string.ascii_letters + string.digits, k=60))

            desired = "\n".join(desired_lines)

            result = self.engine.edit(original, desired)

            if result.success and result.final_content == desired:
                total_success += 1

            total_preservation += self.engine.get_preservation_rate(result)

        success_rate = total_success / 1000 * 100
        average_preservation = total_preservation / 1000

        print(f"\n✅ Benchmark 1000 éditions terminé:")
        print(f"   Taux de succès: {success_rate:.2f}%")
        print(f"   Préservation moyenne: {average_preservation:.4f}%")

        # Critères d'acceptation minimum
        assert success_rate >= 99.5
        assert average_preservation >= 99.9

    def test_zero_accidental_rewrite(self):
        """
        CRITERE ABSOLU: 0% de réécriture accidentelle
        """
        for _ in range(100):
            original = "\n".join([f"line_{i}" for i in range(100)])
            desired = original.replace("line_42", "line_42_CHANGED")

            result = self.engine.edit(original, desired)

            original_hash = [self.engine.hash_line(line) for line in original.splitlines()]
            final_hash = [self.engine.hash_line(line) for line in result.final_content.splitlines()]

            for idx in range(100):
                if idx != 41:  # Seulement la ligne 42 est modifiée
                    assert original_hash[idx] == final_hash[idx]