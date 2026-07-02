"""Module-level config dataclass. No matplotlib imports, no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field, fields


@dataclass
class Config:
    """Global catplotlib configuration, mutated by api.py and read by render/hook.py."""

    enabled: bool = True
    style: str | list[str] = "mix"
    density: str = "normal"
    seed: int | None = None

    def snapshot(self) -> dict[str, object]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def restore(self, snapshot: dict[str, object]) -> None:
        for name, value in snapshot.items():
            setattr(self, name, value)

    def update(self, **overrides: object) -> None:
        valid = {f.name for f in fields(self)}
        for name, value in overrides.items():
            if name not in valid:
                raise TypeError(f"Unknown config option: {name}")
            setattr(self, name, value)


_config: Config = field(default_factory=Config)
_CONFIG = Config()


def get_config() -> Config:
    return _CONFIG
