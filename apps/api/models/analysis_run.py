import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from core.database import Base


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        SAEnum(AnalysisStatus, native_enum=False),
        default=AnalysisStatus.pending,
        nullable=False,
    )

    raw_input: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    normalized_tree: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    design_tokens: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_interpretation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_code: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="analyses")  # noqa: F821
