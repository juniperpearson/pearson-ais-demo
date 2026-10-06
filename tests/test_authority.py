import unittest

from demo import ExecutionLease, MVSO


class TestAISAuthority(unittest.TestCase):

    def make_authorized_mvso(self):
        mvso = MVSO()

        lease = ExecutionLease(
            lease_id="ELO-E1",
            epoch=1,
        )

        mvso.active_lease = lease

        return mvso, lease

    def test_valid_initial_authority(self):
        """
        A committed lease for the current epoch should
        permit authority when no veto or containment exists.
        """

        mvso, lease = self.make_authorized_mvso()

        self.assertTrue(
            mvso.authority_valid(lease)
        )

    def test_old_lease_fails_after_containment(self):
        """
        A lease from a previous Authority Epoch must not
        survive a Logical Zero containment boundary.
        """

        mvso, old_lease = self.make_authorized_mvso()

        mvso.evaluate_action(
            "DELETE_PROTECTED_RECORD"
        )

        self.assertEqual(
            mvso.authority_epoch,
            2,
        )

        self.assertFalse(
            mvso.authority_valid(old_lease)
        )

    def test_fault_resolution_does_not_restore_authority(self):
        """
        Removing the triggering fault must not restore
        execution authority automatically.
        """

        mvso, old_lease = self.make_authorized_mvso()

        mvso.evaluate_action(
            "DELETE_PROTECTED_RECORD"
        )

        mvso.resolve_fault()

        self.assertFalse(
            mvso.authority_valid(old_lease)
        )

    def test_fresh_lease_requires_commit(self):
        """
        A current-epoch ELO must not grant authority until
        guarded LeaseCommit succeeds.
        """

        mvso, _ = self.make_authorized_mvso()

        mvso.evaluate_action(
            "DELETE_PROTECTED_RECORD"
        )

        mvso.resolve_fault()

        self.assertTrue(
            mvso.revalidate()
        )

        new_lease = mvso.issue_new_lease()

        # Fresh lease exists but is not committed.
        self.assertFalse(
            mvso.authority_valid(new_lease)
        )

        # Guarded commit restores authority.
        self.assertTrue(
            mvso.commit_lease(new_lease)
        )

        self.assertTrue(
            mvso.authority_valid(new_lease)
        )


if __name__ == "__main__":
    unittest.main()