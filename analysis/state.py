from dataclasses import dataclass, field


@dataclass
class SolverState:
    mapping: dict = field(default_factory=dict)
    plaintext: str = ""
    score: int = 0

    remember: dict = field(default_factory=dict)
    history: list = field(default_factory=list)

    def copy(self):
        return SolverState(
            mapping=self.mapping.copy(),
            plaintext=self.plaintext,
            score=self.score,
            remember=self.remember.copy(),
            history=self.history.copy(),
        )