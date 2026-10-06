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
        reasons = []

        if not self.governance_integrity:
            reasons.append("governance integrity failure")

        if self.hard_veto:
            reasons.append("Layer B hard veto active")

        if self.logical_zero:
            reasons.append("Logical Zero containment latched")

        if lease is None:
            reasons.append("no execution lease")

        elif lease.epoch != self.authority_epoch:
            reasons.append(
                f"epoch mismatch: lease={lease.epoch}, current={self.authority_epoch}"
            )

        authorized = len(reasons) == 0

        if authorized:
            print("[AUTHORITY] GRANTED")
        else:
            print("[AUTHORITY] DENIED")
            for reason in reasons:
                print(f"            - {reason}")

        return authorized

    def evaluate_action(self, action):
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
        print("[MVSO] Autonomous authority revoked")

        self.logical_zero = True

        old_epoch = self.authority_epoch
        self.authority_epoch += 1

        print("[LOGICAL ZERO] Containment latched")
        print(
            f"[EPOCH] Authority Epoch advanced: "
            f"{old_epoch} -> {self.authority_epoch}"
        )

    def resolve_fault(self):
        print("\n[RECOVERY] Triggering condition resolved")

        self.hard_veto = False

        print(
            "[RECOVERY] Fault cleared, but authority remains revoked"
        )

    def layer_c_eligible(self):
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
        if not self.layer_c_eligible():
            return False

        print("[D_R] Collecting fresh post-containment evidence")
        print("[D_R] Revalidation PASS")

        self.revalidation_passed = True
        return True

    def issue_new_lease(self):
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
        if lease is None:
            print("[LEASE COMMIT] DENIED: no lease")
            return False

        if lease.epoch != self.authority_epoch:
            print("[LEASE COMMIT] DENIED: stale epoch")
            return False

        if not self.revalidation_passed:
            print("[LEASE COMMIT] DENIED: revalidation incomplete")
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

    # Initial authority
    old_lease = ExecutionLease(
        lease_id="ELO-E1",
        epoch=1,
    )

    mvso.active_lease = old_lease

    print("\n[START] Actor holds valid Epoch 1 execution authority")
    mvso.authority_valid(old_lease)

    # Actor requests something prohibited
    mvso.evaluate_action("DELETE_PROTECTED_RECORD")

    print("\n[ACTOR] Attempting execution with old ELO")
    mvso.authority_valid(old_lease)

    # Fault disappears
    mvso.resolve_fault()

    print("\n[ACTOR] Attempting immediate resume")
    mvso.authority_valid(old_lease)

    # Formal recovery path
    mvso.revalidate()

    new_lease = mvso.issue_new_lease()

    print("\n[ACTOR] Fresh lease exists, but has not been committed")
    mvso.authority_valid(new_lease)

    # Guarded lease commit
    mvso.commit_lease(new_lease)

    print("\n[ACTOR] Testing authority after guarded recovery")
    mvso.authority_valid(new_lease)

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print(
        "Fault resolution did not restore authority.\n"
        "Fresh authority required revalidation, "
        "a current-epoch ELO, and LeaseCommit."
    )
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
