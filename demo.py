"""
Pearson AIS Protocol v2.0
Minimal Runtime Authority Governance Demo

Pedagogical reference implementation only.
This is not a production safety system.
"""

from dataclasses import dataclass


PROHIBITED_ACTIONS = {
    "DELETE_PROTECTED_RECORD",
}


@dataclass
class ExecutionLease:
    lease_id: str
    epoch: int


class MVSO:
    """
    Minimal simulation of the AIS Minimum Viable Secondary Observer.

    The MVSO determines whether the actor currently possesses
    valid execution authority.
    """

    def __init__(self):
        self.governance_integrity = True
        self.hard_veto = False
        self.logical_zero = False
        self.authority_epoch = 1
        self.revalidation_passed = False
        self.active_lease = None

    def authority_valid(self, lease):
        """
        Runtime authority exists only when all required conditions hold.

        Simplified AIS authority model:

        Authority =
            GovernanceIntegrity
            AND NOT HardVeto
            AND NOT LogicalZero
            AND LeaseValid
        """

        reasons = []

        if not self.governance_integrity:
            reasons.append("governance integrity failure")

        if self.hard_veto:
            reasons.append("Layer B hard veto active")

        if self.logical_zero:
            reasons.append("Logical Zero containment latched")

        if lease is None:
            reasons.append("no execution lease")

        else:
            if lease.epoch != self.authority_epoch:
                reasons.append(
                    f"epoch mismatch: "
                    f"lease={lease.epoch}, current={self.authority_epoch}"
                )

            if self.active_lease is None:
                reasons.append("no committed execution lease")

            elif lease.lease_id != self.active_lease.lease_id:
                reasons.append("lease has not been committed")

        authorized = len(reasons) == 0

        if authorized:
            print("[AUTHORITY] GRANTED")
        else:
            print("[AUTHORITY] DENIED")

            for reason in reasons:
                print(f"            - {reason}")

        return authorized

    def evaluate_action(self, action):
        """
        Evaluate an actor request against the simplified hard-invariant set.
        """

        print(f"\n[ACTOR] Requested action: {action}")

        if action in PROHIBITED_ACTIONS:
            print("[IGO] Hard invariant violation detected")
            print("[LAYER B] VETO = TRUE")

            self.hard_veto = True
            self.enter_logical_zero()

            return False

        print("[IGO] No hard invariant violation")

        return True

    def enter_logical_zero(self):
        """
        Revoke mission authority and advance the protected Authority Epoch.
        """

        print("[MVSO] Autonomous authority revoked")

        self.logical_zero = True

        # Containment destroys currently committed runtime authority.
        self.active_lease = None

        old_epoch = self.authority_epoch
        self.authority_epoch += 1

        print("[LOGICAL ZERO] Containment latched")

        print(
            f"[EPOCH] Authority Epoch advanced: "
            f"{old_epoch} -> {self.authority_epoch}"
        )

    def resolve_fault(self):
        """
        Remove the triggering fault without restoring execution authority.
        """

        print("\n[RECOVERY] Triggering condition resolved")

        self.hard_veto = False

        print(
            "[RECOVERY] Fault cleared, but authority remains revoked"
        )

    def layer_c_eligible(self):
        """
        Determine whether the system may attempt post-containment
        revalidation.

        Layer C does not restore authority.
        """

        eligible = (
            self.governance_integrity
            and not self.hard_veto
            and self.logical_zero
        )

        if eligible:
            print("[LAYER C] Restoration eligibility satisfied")
        else:
            print("[LAYER C] Restoration eligibility denied")

        return eligible

    def revalidate(self):
        """
        Collect simplified post-containment evidence while authority
        remains revoked.
        """

        if not self.layer_c_eligible():
            return False

        print("[D_R] Collecting fresh post-containment evidence")
        print("[D_R] Revalidation PASS")

        self.revalidation_passed = True

        return True

    def issue_new_lease(self):
        """
        Issue a new Execution Lease Object for the current Authority Epoch.

        Possessing the lease alone does not restore authority.
        It must still pass guarded LeaseCommit.
        """

        if not self.revalidation_passed:
            print("[ELO] DENIED: revalidation incomplete")
            return None

        lease = ExecutionLease(
            lease_id=f"ELO-E{self.authority_epoch}",
            epoch=self.authority_epoch,
        )

        print(
            f"[ELO] Fresh execution lease issued "
            f"for Epoch {lease.epoch}"
        )

        return lease

    def commit_lease(self, lease):
        """
        Guarded authority restoration step.
        """

        if lease is None:
            print("[LEASE COMMIT] DENIED: no lease")
            return False

        if lease.epoch != self.authority_epoch:
            print("[LEASE COMMIT] DENIED: stale epoch")
            return False

        if not self.revalidation_passed:
            print(
                "[LEASE COMMIT] DENIED: "
                "revalidation incomplete"
            )
            return False

        if self.hard_veto:
            print("[LEASE COMMIT] DENIED: hard veto active")
            return False

        if not self.governance_integrity:
            print(
                "[LEASE COMMIT] DENIED: "
                "governance integrity failure"
            )
            return False

        self.active_lease = lease
        self.logical_zero = False
        self.revalidation_passed = False

        print("[LEASE COMMIT] SUCCESS")

        return True


def run_demo():
    print("=" * 60)
    print("PEARSON AIS v2.0 — MINIMAL AUTHORITY DEMO")
    print("=" * 60)

    mvso = MVSO()

    # ---------------------------------------------------------
    # 1. Actor begins with valid authority under Epoch 1
    # ---------------------------------------------------------

    old_lease = ExecutionLease(
        lease_id="ELO-E1",
        epoch=1,
    )

    mvso.active_lease = old_lease

    print(
        "\n[START] Actor holds valid Epoch 1 execution authority"
    )

    mvso.authority_valid(old_lease)

    # ---------------------------------------------------------
    # 2. Actor attempts a prohibited action
    # ---------------------------------------------------------

    mvso.evaluate_action(
        "DELETE_PROTECTED_RECORD"
    )

    # ---------------------------------------------------------
    # 3. Actor attempts to reuse its old lease
    # ---------------------------------------------------------

    print(
        "\n[ACTOR] Attempting execution with old ELO"
    )

    mvso.authority_valid(old_lease)

    # ---------------------------------------------------------
    # 4. Triggering fault disappears
    # ---------------------------------------------------------

    mvso.resolve_fault()

    print(
        "\n[ACTOR] Attempting immediate resume"
    )

    mvso.authority_valid(old_lease)

    # ---------------------------------------------------------
    # 5. Formal recovery path begins
    # ---------------------------------------------------------

    mvso.revalidate()

    # ---------------------------------------------------------
    # 6. Current-epoch lease is issued
    # ---------------------------------------------------------

    new_lease = mvso.issue_new_lease()

    print(
        "\n[ACTOR] Fresh lease exists, "
        "but has not been committed"
    )

    mvso.authority_valid(new_lease)

    # ---------------------------------------------------------
    # 7. Guarded LeaseCommit restores authority
    # ---------------------------------------------------------

    mvso.commit_lease(new_lease)

    print(
        "\n[ACTOR] Testing authority after guarded recovery"
    )

    mvso.authority_valid(new_lease)

    # ---------------------------------------------------------
    # Complete
    # ---------------------------------------------------------

    print("\n" + "=" * 60)

    print("DEMO COMPLETE")

    print(
        "Fault resolution did not restore authority."
    )

    print(
        "Fresh authority required revalidation, "
        "a current-epoch ELO, and LeaseCommit."
    )

    print("=" * 60)


if __name__ == "__main__":
    run_demo()
